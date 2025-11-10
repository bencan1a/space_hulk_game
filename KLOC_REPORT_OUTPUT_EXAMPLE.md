# KLOC Report - Sample Output

This document shows the expected output format when running `kloc-report.py` with authentication.

## Console Output Example

```
Time window: 2025-11-01 to 2025-11-09 (America/Denver)  →  UTC [2025-11-01T06:00:00Z .. 2025-11-10T05:59:59Z]
Scanning 8 repositories...
[bencan1a/repo1] total commits: 15
[bencan1a/repo2] total commits: 23
[bencan1a/repo3-fork] total commits: 5
[bencan1a/space_hulk_game] total commits: 42

=== Summary ===
Churn (adds+deletes): 8543 lines (~8.5 KLOC)
Tests churn: 1234   Impl churn: 7309
Percent tests: 14.5%
Per-file CSV: kloc_files.csv
Per-repo CSV: kloc_by_repo.csv
```

## CSV Output: kloc_files.csv

```csv
repo,sha,file,adds,dels,is_test
bencan1a/space_hulk_game,abc123,src/main.py,45,12,false
bencan1a/space_hulk_game,abc123,tests/test_main.py,67,5,true
bencan1a/space_hulk_game,def456,src/utils.py,23,8,false
bencan1a/repo1,ghi789,app.js,102,45,false
```

## CSV Output: kloc_by_repo.csv

```csv
repo,adds_tests,dels_tests,adds_impl,dels_impl,tests_churn,impl_churn,percent_tests
bencan1a/space_hulk_game,234,89,1567,432,323,1999,13.9
bencan1a/repo1,145,23,2345,678,168,3023,5.3
bencan1a/repo2,98,12,567,234,110,801,12.1
bencan1a/repo3-fork,45,8,123,45,53,168,24.0
```

## Key Features Demonstrated

1. **Includes Forks**: Notice `repo3-fork` is included in the analysis
2. **All Commits**: Analyzes all commits in the time window, not filtered by specific users
3. **Test vs Implementation Split**: Files are categorized based on path patterns
4. **Summary Statistics**: Total churn in KLOC with test percentage
5. **Per-File Detail**: Every changed file is tracked with additions/deletions
6. **Per-Repo Aggregation**: Summary statistics rolled up by repository

## Notes

- The actual output will vary based on the repositories owned by the specified user
- Forks are now included (previously filtered out)
- All commits are analyzed (previously only commits by specific users)
- The script handles pagination automatically for large result sets
- Rate limiting is managed with automatic retry logic
