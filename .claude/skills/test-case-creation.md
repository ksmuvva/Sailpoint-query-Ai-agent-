# SailPoint Test Case Creation

Description: Generate structured test cases for SailPoint implementation testing
Trigger: When the user asks for test cases, test scenarios, test plans, or QA documentation

## Instructions

When creating test cases:

1. **Identify the test scope**: What feature/component is being tested?
   - BeanShell rule logic
   - Connector operations (aggregation, provisioning)
   - Identity lifecycle (JML)
   - Certification campaigns
   - Access request workflows
   - SOD policy enforcement
2. **Determine test type**: Unit, Integration, UAT, E2E, Regression
3. **Search for requirements**: Use sailpoint_web_search to find expected behavior documentation
4. **Generate structured test cases** with all required fields
5. **Include edge cases**: Null values, boundary conditions, error scenarios

## Response Template

### Test Plan: [Feature Name]

**Test Scope:** [What is being tested]
**Product:** [IIQ / ISC]
**Test Type:** [Unit / Integration / UAT / E2E]

### Test Cases

| TC-ID | Title | Category | Priority |
|-------|-------|----------|----------|
| TC-001 | [Title] | [Category] | [High/Medium/Low] |

---

#### TC-001: [Title]

**Description:** [What this test verifies]

**Preconditions:**
- [Required setup]

**Test Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result:**
[What should happen]

**Priority:** [High/Medium/Low]

---

### Coverage Matrix
| Scenario | Positive | Negative | Edge Case |
|----------|----------|----------|-----------|
| [Scenario] | TC-001 | TC-002 | TC-003 |

### Sources
- [Reference](URL)

## Standard Categories
- Positive: Verify correct behavior with valid inputs
- Negative: Verify error handling with invalid inputs
- Edge Case: Verify boundary conditions and unusual scenarios
- Regression: Verify no existing functionality is broken
- Performance: Verify response times and resource usage
