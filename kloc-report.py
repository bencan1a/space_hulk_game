"""
Aggregates commit diff stats (adds+deletes = "churn") across all repos owned by a GitHub user,
including forks, within a date window. Analyzes ALL commits to those repos (not filtered by author).
Splits totals into "tests" vs "implementation" using filename/path patterns, and writes a per-file 
CSV plus an optional per-repo summary.

Usage:
  python kloc-report.py --user bencan1a                # last Sunday 00:00 (America/Denver) to today 23:59:59
  python kloc-report.py --user bencan1a --since 2025-11-02 --until 2025-11-09
  python kloc-report.py --user bencan1a --owner-scope user  # (default) scan repos under the user account
  python kloc-report.py --user bencan1a --owner-scope org   # scan repos under an org named --org <name>
  python kloc-report.py --user bencan1a --org YourOrg --owner-scope org

Auth:
  Uses a GitHub token from env var GH_TOKEN or GITHUB_TOKEN (recommended to avoid low rate limits).
"""

import argparse
import csv
import datetime as dt
import os
import re
import sys
import time
from typing import Dict, Iterable, List, Optional, Tuple
import requests

# -------- Configuration: test & ignore patterns (adjust to your stack) --------
TEST_RE = re.compile(r'(^|/)(test|tests|__tests__|spec|specs)/|(^|/).*(_test|\.(spec|test))\.', re.I)
IGNORE_RE = re.compile(r'(^|/)(node_modules|dist|build|target|vendor|\.venv|\.git|coverage|out)/|(\.lock$|\.min\.js$|\.map$|\.svg$|\.png$|\.jpe?g$|\.gif$|\.pdf$|\.zip$)', re.I)

# -------- Helpers --------
def get_token() -> Optional[str]:
    return os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

def gh_headers() -> Dict[str, str]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "kloc-report-script"}
    tok = get_token()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    return headers

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--user", required=True, help="GitHub username (e.g., bencan1a) to scan all public repos for.")
    p.add_argument("--org", help="If --owner-scope=org, name of the organization to scan (e.g., Alteryx).")
    p.add_argument("--owner-scope", choices=["user","org"], default="user",
                   help="Scan repos owned by user (default) or by org (requires --org).")
    p.add_argument("--since", help="Start date YYYY-MM-DD in America/Denver local time (00:00:00). Defaults to last Sunday.")
    p.add_argument("--until", help="End date YYYY-MM-DD in America/Denver local time (23:59:59). Defaults to today.")
    p.add_argument("--out-files-csv", default="kloc_files.csv", help="Per-file CSV output path.")
    p.add_argument("--out-repos-csv", default="kloc_by_repo.csv", help="Per-repo CSV output path (aggregated).")
    p.add_argument("--sleep", type=float, default=0.3, help="Sleep between API calls to be gentle on rate limits.")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()

# America/Denver handling (no zoneinfo on Py<3.9 fallback)
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    ZoneInfo = None

def denver_tz():
    if ZoneInfo is not None:
        return ZoneInfo("America/Denver")
    # Fallback: naive approximation (MT/MST) without DST awareness
    class _Denver(dt.tzinfo):
        def utcoffset(self, d): return dt.timedelta(hours=-7)
        def tzname(self, d): return "America/Denver"
        def dst(self, d): return dt.timedelta(0)
    return _Denver()

def last_sunday_window_utc() -> Tuple[str, str, str]:
    """Compute [since, until] in UTC ISO (Z) covering last Sunday 00:00 (Denver) to today 23:59:59 (Denver)."""
    now = dt.datetime.now(tz=denver_tz())
    # If today is Sunday, "last Sunday" is 7 days ago
    days_since_sun = (now.weekday() + 1) % 7  # Monday=0, Sunday=6 â this maps Sun to 0, Mon to 1, ...
    days_back = 7 if days_since_sun == 0 else days_since_sun
    last_sun = (now - dt.timedelta(days=days_back)).replace(hour=0, minute=0, second=0, microsecond=0)
    today_eod = now.replace(hour=23, minute=59, second=59, microsecond=0)

    since_utc = last_sun.astimezone(dt.timezone.utc).isoformat().replace("+00:00","Z")
    until_utc = today_eod.astimezone(dt.timezone.utc).isoformat().replace("+00:00","Z")
    # For printing
    label = f"{last_sun.date()} to {today_eod.date()} (America/Denver)"
    return since_utc, until_utc, label

def local_dates_to_utc_range(since_local: str, until_local: str) -> Tuple[str, str, str]:
    tz = denver_tz()
    s = dt.datetime.strptime(since_local, "%Y-%m-%d").replace(tzinfo=tz)
    u = dt.datetime.strptime(until_local, "%Y-%m-%d").replace(tzinfo=tz)
    s = s.replace(hour=0, minute=0, second=0, microsecond=0)
    u = u.replace(hour=23, minute=59, second=59, microsecond=0)
    return (
        s.astimezone(dt.timezone.utc).isoformat().replace("+00:00","Z"),
        u.astimezone(dt.timezone.utc).isoformat().replace("+00:00","Z"),
        f"{s.date()} to {u.date()} (America/Denver)"
    )

def gh_paginated(url: str, params: Dict[str, str]) -> Iterable[dict]:
    """Yield all JSON items across pages for endpoints that return a list and use Link headers."""
    headers = gh_headers()
    while url:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            reset = resp.headers.get("X-RateLimit-Reset")
            wait = max(5, int(reset) - int(time.time())) if reset and reset.isdigit() else 60
            print(f"Rate-limited. Sleeping {wait}s...", file=sys.stderr)
            time.sleep(wait); continue
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            # Some endpoints return an object (e.g., search). Assume 'items' pattern (not used here).
            data = data.get("items", [])
        for item in data:
            yield item
        # Parse Link header for next
        link = resp.headers.get("Link","")
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                next_url = part[part.find("<")+1:part.find(">")]
                break
        url = next_url
        # After first page, params must be None so we don't duplicate them
        params = {}

def list_repos_user(user: str) -> List[str]:
    # https://api.github.com/users/{user}/repos
    url = f"https://api.github.com/users/{user}/repos"
    repos = []
    for repo in gh_paginated(url, {"per_page": "100", "type": "owner", "sort": "full_name"}):
        # Include forks in the analysis
        full = repo.get("full_name")
        if full: repos.append(full)
    return repos

def list_repos_org(org: str) -> List[str]:
    # https://api.github.com/orgs/{org}/repos
    url = f"https://api.github.com/orgs/{org}/repos"
    repos = []
    for repo in gh_paginated(url, {"per_page": "100", "type": "all", "sort": "full_name"}):
        # Include forks in the analysis
        full = repo.get("full_name")
        if full: repos.append(full)
    return repos

def is_copilot_commit(commit_obj: dict) -> bool:
    # Heuristics: author/committer login == github-copilot; author/committer name == "GitHub Copilot";
    # commit message contains "Co-authored-by: GitHub Copilot"
    a = commit_obj.get("author") or {}
    c = commit_obj.get("committer") or {}
    ca = commit_obj.get("commit", {}).get("author", {}) or {}
    cc = commit_obj.get("commit", {}).get("committer", {}) or {}
    msg = commit_obj.get("commit", {}).get("message", "") or ""

    login_matches = (a.get("login") == "github-copilot") or (c.get("login") == "github-copilot")
    name_matches = (ca.get("name") == "GitHub Copilot") or (cc.get("name") == "GitHub Copilot")
    trailer = bool(re.search(r"Co-authored-by:\s*GitHub\s+Copilot", msg, flags=re.I))
    return login_matches or name_matches or trailer

def commit_matches_user_or_copilot(commit_obj: dict, user: str) -> bool:
    a = commit_obj.get("author") or {}
    c = commit_obj.get("committer") or {}
    return (
        a.get("login") == user or
        c.get("login") == user or
        is_copilot_commit(commit_obj)
    )

def list_commits_for_repo(full_name: str, since_iso: str, until_iso: str, user: str, sleep_s: float, verbose=False) -> List[dict]:
    # https://api.github.com/repos/{owner}/{repo}/commits?since=&until=
    url = f"https://api.github.com/repos/{full_name}/commits"
    params = {"since": since_iso, "until": until_iso, "per_page": "100"}
    commits = []
    for c in gh_paginated(url, params):
        # Include all commits to the repo (not filtering by user)
        commits.append(c)
        if sleep_s: time.sleep(sleep_s)
    if verbose:
        print(f"[{full_name}] total commits: {len(commits)}", file=sys.stderr)
    return commits

def get_commit_detail(full_name: str, sha: str, sleep_s: float) -> dict:
    url = f"https://api.github.com/repos/{full_name}/commits/{sha}"
    resp = requests.get(url, headers=gh_headers())
    if resp.status_code == 403 and "rate limit" in resp.text.lower():
        reset = resp.headers.get("X-RateLimit-Reset")
        wait = max(5, int(reset) - int(time.time())) if reset and reset.isdigit() else 60
        print(f"Rate-limited. Sleeping {wait}s...", file=sys.stderr)
        time.sleep(wait)
        resp = requests.get(url, headers=gh_headers())
    resp.raise_for_status()
    if sleep_s: time.sleep(sleep_s)
    return resp.json()

def main():
    args = parse_args()

    if args.owner_scope == "org" and not args.org:
        print("--owner-scope=org requires --org <name>", file=sys.stderr)
        sys.exit(2)

    # Compute window
    if args.since and args.until:
        since_iso, until_iso, label = local_dates_to_utc_range(args.since, args.until)
    else:
        since_iso, until_iso, label = last_sunday_window_utc()

    print(f"Time window: {label}  â  UTC [{since_iso} .. {until_iso}]")

    # Enumerate repos
    if args.owner_scope == "org":
        repos = list_repos_org(args.org)
    else:
        repos = list_repos_user(args.user)

    if not repos:
        print("No repositories found to scan.", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {len(repos)} repositories...")

    # Open CSVs
    files_out = open(args.out_files_csv, "w", newline="", encoding="utf-8")
    files_writer = csv.writer(files_out)
    files_writer.writerow(["repo","sha","file","adds","dels","is_test"])

    # Per-repo aggregates
    agg: Dict[str, Dict[str, int]] = {}

    total_add_tests = total_del_tests = 0
    total_add_impl  = total_del_impl  = 0

    for full in repos:
        commits = list_commits_for_repo(full, since_iso, until_iso, args.user, args.sleep, args.verbose)
        if not commits:
            continue

        for c in commits:
            sha = c.get("sha")
            if not sha:
                continue
            detail = get_commit_detail(full, sha, args.sleep)
            files = detail.get("files") or []
            for f in files:
                path = f.get("filename","")
                adds = int(f.get("additions",0) or 0)
                dels = int(f.get("deletions",0) or 0)

                # Skip ignored paths / binaries by pattern
                if IGNORE_RE.search(path):
                    continue

                is_test = bool(TEST_RE.search(path))

                files_writer.writerow([full, sha, path, adds, dels, str(is_test).lower()])

                # Accumulate totals
                if is_test:
                    total_add_tests += adds
                    total_del_tests += dels
                else:
                    total_add_impl += adds
                    total_del_impl += dels

                # Per-repo
                a = agg.setdefault(full, {"adds_t":0,"dels_t":0,"adds_i":0,"dels_i":0})
                if is_test:
                    a["adds_t"] += adds; a["dels_t"] += dels
                else:
                    a["adds_i"] += adds; a["dels_i"] += dels

    files_out.close()

    # Write per-repo CSV
    with open(args.out_repos_csv, "w", newline="", encoding="utf-8") as g:
        w = csv.writer(g)
        w.writerow(["repo","adds_tests","dels_tests","adds_impl","dels_impl","tests_churn","impl_churn","percent_tests"])
        for repo, a in sorted(agg.items()):
            tests_churn = a["adds_t"] + a["dels_t"]
            impl_churn  = a["adds_i"] + a["dels_i"]
            denom = tests_churn + impl_churn
            pct = (tests_churn*100.0/denom) if denom else 0.0
            w.writerow([repo, a["adds_t"], a["dels_t"], a["adds_i"], a["dels_i"], tests_churn, impl_churn, f"{pct:.1f}"])

    # Print overall summary
    total_add = total_add_tests + total_add_impl
    total_del = total_del_tests + total_del_impl
    churn = total_add + total_del
    pct_tests = ( (total_add_tests + total_del_tests) * 100.0 / churn ) if churn else 0.0

    print("\n=== Summary ===")
    print(f"Churn (adds+deletes): {churn} lines (~{churn/1000:.1f} KLOC)")
    print(f"Tests churn: {total_add_tests + total_del_tests}   Impl churn: {total_add_impl + total_del_impl}")
    print(f"Percent tests: {pct_tests:.1f}%")
    print(f"Per-file CSV: {args.out_files_csv}")
    print(f"Per-repo CSV: {args.out_repos_csv}")

if __name__ == "__main__":
    # Friendly hint if unauthenticated
    if not get_token():
        print("Warning: No GH_TOKEN/GITHUB_TOKEN found. You may hit rate limits. Set GH_TOKEN to a personal access token.", file=sys.stderr)
    try:
        main()
    except requests.HTTPError as e:
        print(f"GitHub API error: {e} -> {getattr(e.response, 'text', '')[:300]}", file=sys.stderr)
        sys.exit(1)
