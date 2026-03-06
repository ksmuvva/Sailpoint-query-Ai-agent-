# SailPoint High-Level Design (HLD)

Description: Generate architecture-level design documents for SailPoint implementations
Trigger: When the user asks for high-level design, architecture overview, or system design

## Instructions

When creating an HLD:

1. **Understand requirements**: What systems, integrations, and features are needed?
2. **Research architecture patterns**: Use sailpoint_web_search for SailPoint architecture guides
3. **Design the solution** covering these areas:
   - System topology and component interactions
   - Integration patterns for connected systems
   - Data flow architecture
   - Security architecture
   - Deployment strategy
4. **Include diagrams**: ASCII-based architecture diagrams
5. **Address cross-cutting concerns**: HA, DR, performance, security

## Response Template

### High-Level Design: [Project Name]

**Version:** 1.0
**Product:** [IIQ / ISC]

---

### 1. Executive Summary
[Brief overview of the solution]

### 2. Architecture Overview
```
[ASCII architecture diagram]
```

### 3. System Components
| Component | Purpose | Technology |
|-----------|---------|------------|
| [Component] | [Purpose] | [Tech] |

### 4. Integration Architecture
| Source System | Direction | Target System | Protocol |
|--------------|-----------|---------------|----------|
| [System] | --> | [System] | [Protocol] |

### 5. Data Flow
```
[ASCII data flow diagram]
```

### 6. Security Architecture
- Authentication: [Method]
- Authorization: [Model]
- Data Protection: [Approach]

### 7. Deployment Architecture
- Environment: [On-prem / Cloud / Hybrid]
- HA Strategy: [Approach]
- DR Strategy: [Approach]

### 8. Non-Functional Requirements
| NFR | Requirement | Approach |
|-----|-------------|----------|
| Performance | [Target] | [How] |
| Scalability | [Target] | [How] |
| Availability | [Target] | [How] |

### Sources
- [Reference](URL)
