# SailPoint Research

Description: Search and synthesize SailPoint documentation to answer questions about features, concepts, and configurations
Trigger: When the user asks questions about SailPoint features, concepts, configurations, or best practices

## Instructions

When researching SailPoint topics:

1. **Identify the product scope**: Is this about IIQ (on-prem), ISC/IDN (cloud), or both?
2. **Search official sources first**:
   - Use sailpoint_web_search to search developer.sailpoint.com
   - Use sailpoint_web_search to search documentation.sailpoint.com
   - Use sailpoint_web_search to search community.sailpoint.com
3. **Fetch detailed content**: Use doc_retriever to get full page content from promising URLs
4. **Cross-reference**: Verify information across multiple sources
5. **Synthesize**: Combine findings into a clear, structured answer

## Response Template

### [Topic Name]

[Clear explanation of the concept/feature]

### Key Points
- [Important detail 1]
- [Important detail 2]
- [Important detail 3]

### Product-Specific Details

**IdentityIQ (On-Premise):**
- [IIQ-specific information]

**Identity Security Cloud (Cloud):**
- [ISC-specific information]

### Configuration / Setup
[Step-by-step guidance if applicable]

### Sources
- [Source 1](URL)
- [Source 2](URL)

## Search Strategy
- Start with official SailPoint documentation
- Check community forums for practical guidance and edge cases
- Look at GitHub examples for code samples
- Fall back to broader IAM resources for general concepts
