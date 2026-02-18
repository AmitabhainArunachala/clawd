# Test Report: Fix Test File Paths

## Task ID: Fix test file paths

### Status: Some Tests Failed

**Summary:**
- Total Tests Run: 54
- Passed: 52
- Failed: 2

### Failed Tests:
1. **test_send_to_discord**: 
   - Failure Reason: Discord not configured.
2. **test_poll_discord**:
   - Failure Reason: Expected message count did not match.

### Next Steps:
- Review configurations for Discord integration before re-running the tests.

**Note:** The test file paths have been fixed as per the objective, but functionality verification needs further attention regarding Discord integrations.