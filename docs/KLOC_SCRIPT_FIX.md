# KLOC Script Fix - November 2025

## Problem

The `kloc-report.py` script and its GitHub Actions workflow (`run-kloc-report.yml`) were experiencing hanging issues:

1. **Symptom**: Workflow would appear to hang after starting, showing no output
2. **User Action**: Users cancelled the workflow after ~4 minutes thinking it was stuck
3. **Actual Issue**: Script was running but output was buffered, making it appear frozen
4. **Secondary Issue**: No timeout configured, so truly stuck runs could hang indefinitely

## Root Cause Analysis

### Output Buffering
- Python buffers stdout when outputting to a pipe (not a TTY)
- The workflow uses `tee kloc_output.log` which creates a pipe
- Without the `-u` flag, Python uses full buffering (8KB-64KB chunks)
- This meant output only appeared after processing many repos
- To users, this looked like the script had hung

### Workflow Timeout
- No explicit timeout was configured on the job step
- While GitHub Actions has a 6-hour default, it wasn't explicit
- No proper error handling for script failures when using `tee`

### Script Performance
- The script processes ALL repos for a user (bencan1a has dozens)
- For each repo, it fetches ALL commits in the date range
- For each commit, it makes another API call to get file details
- With 0.3s sleep between calls, this legitimately takes time
- Processing 4 repos in 4 minutes before cancellation was normal speed

## Solution Implemented

### 1. Unbuffered Python Output

**Workflow Change**:
```yaml
CMD="python -u kloc-report.py --user bencan1a --verbose"
```

The `-u` flag forces Python to use unbuffered output mode, so progress appears immediately.

### 2. Explicit stdout Flush Calls

**Script Changes** (3 locations):
```python
print(f"Time window: {label}  â  UTC [{since_iso} .. {until_iso}]")
sys.stdout.flush()  # Ensure output is visible immediately
```

Added after key output points:
- Line 211: After printing time window
- Line 224: After printing repo count
- Line 301: After printing final summary

### 3. Explicit Timeout

**Workflow Change**:
```yaml
- name: Run KLOC report script
  timeout-minutes: 360  # 6 hours max (GitHub Actions default)
```

Makes timeout explicit and documents expected maximum runtime.

### 4. Proper Error Handling

**Workflow Change**:
```bash
$CMD 2>&1 | tee kloc_output.log

# Check if script succeeded
SCRIPT_EXIT=${PIPESTATUS[0]}
if [ $SCRIPT_EXIT -ne 0 ]; then
  echo "❌ KLOC report failed with exit code $SCRIPT_EXIT"
  exit $SCRIPT_EXIT
fi
```

Uses `PIPESTATUS[0]` to capture the script's actual exit code before `tee` obscures it.

## Testing

Created comprehensive test coverage:

### Script Tests (`tests/test_kloc_report.py`)
- ✓ Script doesn't hang (timeout checks)
- ✓ Python syntax is valid
- ✓ Unbuffered mode works (`python -u`)
- ✓ Required parameters enforced
- ✓ Flush calls present (3+ instances)
- ✓ Graceful token handling

### Workflow Tests (`tests/test_kloc_workflow.py`)
- ✓ Valid YAML syntax
- ✓ Timeout configured (360 minutes)
- ✓ Unbuffered Python usage
- ✓ Exit code checking logic
- ✓ Required permissions set

**Result**: All 11 tests pass ✓

## Impact

### Before
- Script appeared to hang with no output
- Users cancelled after 4 minutes
- No way to know if actually stuck or just slow
- Errors could be silently ignored

### After
- Real-time progress output visible immediately
- Explicit 6-hour timeout prevents indefinite hangs
- Script failures are properly reported
- Users can see the script is working

### No Functional Changes
- Script logic unchanged
- Same API calls, same data processing
- Same output files and format
- Just visibility and error handling improved

## Expected Behavior

When running the workflow now:

1. ✓ **Immediate feedback**: "Scanning X repositories..." appears right away
2. ✓ **Progress updates**: Per-repo verbose output shows up as processed
3. ✓ **Final summary**: "=== Summary ===" section appears at end
4. ✓ **CSV files**: Both `kloc_files.csv` and `kloc_by_repo.csv` generated
5. ✓ **Proper completion**: Workflow step shows success/failure clearly
6. ✓ **Auto-timeout**: If truly stuck, auto-cancels after 6 hours

## Performance Expectations

The script is expected to run for a **long time** when processing many repos:

- ~4 minutes for 4 repos (observed in logs)
- Estimated **30-60 minutes** for all bencan1a repos (~40-50 repos)
- Variable based on:
  - Number of repos
  - Number of commits in date range
  - GitHub API rate limits
  - Network conditions

**This is normal and expected.** The fix makes the wait visible, not shorter.

## Files Changed

1. `.github/workflows/run-kloc-report.yml`
   - Added `timeout-minutes: 360`
   - Changed to `python -u`
   - Added exit code checking

2. `kloc-report.py`
   - Added 3 `sys.stdout.flush()` calls
   - No logic changes

3. `tests/test_kloc_report.py` (new)
   - 6 tests for script functionality

4. `tests/test_kloc_workflow.py` (new)
   - 5 tests for workflow configuration

## Verification

To verify the fix works:

1. **Run tests locally**:
   ```bash
   python -m unittest tests.test_kloc_report tests.test_kloc_workflow -v
   ```
   Expected: All 11 tests pass

2. **Test script unbuffered mode**:
   ```bash
   python -u kloc-report.py --help
   ```
   Expected: Immediate output, exits cleanly

3. **Trigger workflow**:
   - Go to Actions tab
   - Run "Run KLOC Report" workflow
   - Watch for immediate output in logs
   - Wait for completion (could take 30-60 minutes)

## Related Issues

- GitHub Actions workflow hanging: Fixed ✓
- Script not producing output: Fixed ✓
- No error handling for tee'd commands: Fixed ✓
- Implicit timeout confusing users: Fixed ✓

## References

- Python unbuffered mode: https://docs.python.org/3/using/cmdline.html#cmdoption-u
- GitHub Actions timeout: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepstimeout-minutes
- Bash PIPESTATUS: https://www.gnu.org/software/bash/manual/html_node/Special-Parameters.html

## Performance Optimization - Specific Repos (November 2025)

### Additional Problem
After fixing the buffering issue, it was discovered that the script was still taking 30-60 minutes to complete because it scanned ALL repositories for the user, even though only 5 specific repositories were needed for reporting.

### Solution - Repository Filtering

Added a new `--repos` parameter to allow specifying which repositories to scan:

```bash
python kloc-report.py --user bencan1a --repos CalendarBot space_hulk_game Azahar 3dsconv Python-template
```

**Benefits**:
- **Dramatic speed improvement**: From 30-60 minutes down to ~5 minutes
- **Reduced API calls**: Only queries the specified repositories
- **More predictable runtime**: Scales with number of specified repos, not total repos
- **Flexibility**: Can still scan all repos by omitting the `--repos` parameter

**Workflow Update**:
The workflow now defaults to the 5 specific repositories:
```yaml
CMD="python -u kloc-report.py --user bencan1a --verbose --repos CalendarBot space_hulk_game Azahar 3dsconv Python-template"
```

**Usage**:
- Repo names can be specified with or without the owner prefix
  - `CalendarBot` → automatically becomes `bencan1a/CalendarBot`
  - `bencan1a/CalendarBot` → used as-is
- Multiple repos separated by spaces
- If `--repos` is omitted, scans all repos (original behavior)

**Expected Runtime**:
- With 5 specific repos: ~5 minutes (depending on commit volume)
- With all repos: 30-60 minutes (original behavior)
- Approximately 1 minute per repo for API calls and processing

This optimization addresses the user feedback to reduce run time while maintaining flexibility for different use cases.
