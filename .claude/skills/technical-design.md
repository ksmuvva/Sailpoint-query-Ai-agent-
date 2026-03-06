# SailPoint Technical Design

Description: Generate connector, workflow, provisioning, and integration design specifications
Trigger: When the user asks for connector design, workflow design, provisioning design, or integration architecture

## Instructions

1. **Identify the design type**:
   - Connector design (new application onboarding)
   - Workflow design (business process automation)
   - Provisioning design (account lifecycle operations)
   - Integration design (multi-system architecture)

2. **Research requirements**: Use sailpoint_web_search to find:
   - Target system documentation and APIs
   - SailPoint connector framework docs
   - Similar implementations and best practices

3. **Create the design** with full technical specifications

## Response Template

### Technical Design: [Design Name]

**Design Type:** [Connector / Workflow / Provisioning / Integration]
**Product:** [IIQ / ISC]
**Version:** 1.0

---

### 1. Overview
[What this design covers and its purpose]

### 2. Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-01 | [Requirement] | [Must/Should/Could] |

### 3. Design Specification

#### 3.1 Component Architecture
```
[ASCII diagram]
```

#### 3.2 Configuration
```xml
[Configuration snippet]
```

#### 3.3 Data Mapping
| Source Field | Target Field | Transform | Notes |
|------------|-------------|-----------|-------|
| [field] | [field] | [transform] | [notes] |

### 4. Operations

#### 4.1 Account Aggregation
[How accounts are discovered and imported]

#### 4.2 Account Provisioning
[How accounts are created/updated/disabled/deleted]

#### 4.3 Entitlement Aggregation
[How entitlements (groups, roles) are imported]

### 5. Error Handling
| Scenario | Handling | Alert |
|----------|----------|-------|
| [Error] | [How handled] | [Notification] |

### 6. Testing Plan
| Test | Type | Expected Result |
|------|------|----------------|
| [Test] | [Unit/Integration/UAT] | [Result] |

### Sources
- [Reference](URL)

## Common Design Patterns
- **Hub-and-Spoke**: Central IGA connects to all target systems
- **Direct Connector**: Native connector for standard protocols (LDAP, SCIM, JDBC)
- **Web Service Connector**: REST/SOAP integration for custom APIs
- **Flat File**: CSV/delimited file exchange for legacy systems
- **Cloud Gateway**: VA-mediated access to on-premise systems from ISC
