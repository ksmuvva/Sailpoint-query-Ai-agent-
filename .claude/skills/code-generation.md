# SailPoint Code Generation

Description: Generate production-quality code for SailPoint implementations
Trigger: When the user asks to write, create, or generate code for SailPoint

## Instructions

When generating SailPoint code:

1. **Identify the code type**: BeanShell rule, Java class, XML config, REST API call,
   PowerShell script, ISC Transform JSON, Cloud Rule, or SaaS connector (TypeScript)
2. **Search documentation first**: Use sailpoint_web_search to find relevant API signatures,
   class names, and official examples before writing code
3. **Determine product context**: Is this for IIQ (on-prem) or ISC (cloud)?
   - IIQ: Use `sailpoint.object.*` classes, `SailPointContext`, BeanShell syntax
   - ISC: Use V3 API endpoints, Transform JSON, Cloud Rule sandbox constraints
4. **Generate the code** following these quality standards:
   - Include all required imports explicitly
   - Add inline comments explaining key logic
   - Follow SailPoint naming conventions
   - Handle null checks using `sailpoint.tools.Util` (IIQ) or null-safe patterns
   - Include error handling for common failure scenarios
5. **Provide usage instructions**: How to deploy, configure, and test the code

## Response Template

### [What the code does]
[Brief explanation]

### Prerequisites
- [Required setup]

### Code
```[language]
[Generated code with inline comments]
```

### Deployment Instructions
1. [Step-by-step guide]

### Testing
- [How to verify it works]

### Sources
- [Documentation reference](URL)

## IIQ Rule Types Reference
- BuildMap Rule: transforms connector data during aggregation
- Correlation Rule: matches accounts to identities
- Creation Rule: sets defaults for new identities
- IdentityAttribute Rule: calculates derived attributes
- FieldValue Rule: dynamic provisioning form values
- Certification Rule: customizes certification behavior
- Before/After Provisioning Rule: pre/post provisioning logic

## ISC Code Types Reference
- Transforms: JSON-based data transformations (no code)
- Cloud Rules: Java/BeanShell in sandboxed environment
- SaaS Connectors: TypeScript using @sailpoint/connector-sdk
- Workflows: No-code automation (JSON definitions)
