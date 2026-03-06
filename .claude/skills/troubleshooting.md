# SailPoint Troubleshooting

Description: Diagnose and resolve SailPoint configuration, provisioning, and connector issues
Trigger: When the user asks to debug, diagnose, fix, troubleshoot, or resolve a SailPoint problem

## Instructions

1. **Gather context**: Ask clarifying questions if needed:
   - Which product? (IIQ version or ISC)
   - What operation is failing? (aggregation, provisioning, certification, etc.)
   - What error message or behavior is observed?
   - What was changed recently?

2. **Search for known issues**: Use sailpoint_web_search to check:
   - SailPoint community forums for similar issues
   - SailPoint documentation for correct configuration
   - Known bugs or workarounds for the version

3. **Systematic diagnosis**:
   - Check logs: `sailpoint.log`, `ccg.log`, connector logs
   - Verify configuration: Application XML, Rule code, Workflow steps
   - Test components in isolation
   - Check for common pitfalls (null values, missing imports, incorrect filters)

4. **Provide resolution**:
   - Root cause explanation
   - Step-by-step fix with code/config changes
   - Verification steps to confirm the fix
   - Prevention recommendations

## Response Template

### Issue: [Brief description]

### Root Cause
[Explanation of why this happens]

### Resolution
1. [Step-by-step fix]

### Verification
- [How to confirm the fix works]

### Prevention
- [Best practices to avoid this in the future]

### Sources
- [Reference](URL)

## Common Issue Patterns

### IIQ Issues
- NullPointerException in BeanShell: Missing null checks on `identity.getAttribute()`
- Aggregation failures: Connector config errors, filter syntax, schema mismatch
- Provisioning failures: Missing ProvisioningPlan fields, target system connectivity
- Workflow stuck: Missing transition conditions, approval loops

### ISC Issues
- API 400 errors: Malformed request body, missing required fields
- Transform errors: Invalid transform chain, type mismatches
- VA connectivity: CCG config, firewall rules, certificate issues
- Cloud Rule failures: Sandbox violations, unsupported imports
