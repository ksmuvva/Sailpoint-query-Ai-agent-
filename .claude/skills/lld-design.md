# SailPoint Low-Level Design (LLD)

Description: Generate implementation-level design documents with detailed technical specifications
Trigger: When the user asks for low-level design, implementation spec, or detailed technical design

## Instructions

When creating an LLD:

1. **Reference the HLD**: Understand the high-level architecture context
2. **Research implementation details**: Use sailpoint_web_search for API specs, XML schemas
3. **Design the implementation** covering:
   - Detailed class/module designs
   - Configuration specifications
   - API contracts and data models
   - Rule specifications with input/output
   - Error handling strategies
4. **Include code-level specifications**: Method signatures, data structures

## Response Template

### Low-Level Design: [Component Name]

**Version:** 1.0
**Product:** [IIQ / ISC]

---

### 1. Component Overview
[What this component does and its role in the system]

### 2. Class/Module Design

#### 2.1 [Class/Module Name]
**Purpose:** [What it does]

**Dependencies:**
- [Dependency 1]

**Methods:**
| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| [method] | [params] | [return] | [desc] |

### 3. Configuration Specification

#### 3.1 Application XML
```xml
[XML configuration snippet]
```

#### 3.2 Rule Code
```beanshell
[Rule code with inline comments]
```

### 4. API Contracts
| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| [path] | [verb] | [body] | [body] |

### 5. Data Model
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| [field] | [type] | [Y/N] | [desc] |

### 6. Error Handling
| Error Scenario | Handling | Recovery |
|---------------|----------|----------|
| [Scenario] | [How handled] | [Recovery] |

### 7. Testing Strategy
- Unit tests for: [components]
- Integration tests for: [flows]

### Sources
- [Reference](URL)
