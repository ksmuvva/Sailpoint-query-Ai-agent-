"""SailPoint domain knowledge fragments for prompt augmentation."""

IIQ_KNOWLEDGE = """
## SailPoint IdentityIQ (IIQ) — On-Premise

### Core Objects
- **Identity**: Central identity object (Identity Cube) — attributes, links, roles, entitlements
- **Link**: Account on a target application linked to an identity
- **Application**: Connector configuration for a target system (AD, LDAP, DB, SAP, etc.)
- **Role**: Bundle of entitlements — IT Roles (technical) and Business Roles (organizational)
- **Entitlement**: Fine-grained permission on a target system (AD group, SAP role, etc.)
- **Bundle**: Internal name for Role objects in the data model

### Scripting & Rules
- **BeanShell**: Java-based scripting language for IIQ Rules
- **Rule Types**: BuildMap, Correlation, Creation, IdentityAttribute, FieldValue,
  Certification, BeforeProvisioning, AfterProvisioning, Workflow, Policy, JDBCBuildMap
- **Context Object**: `sailpoint.api.SailPointContext` — access to IIQ object model
- **Utility**: `sailpoint.tools.Util` — null checks, string ops, collection helpers
- **Logger**: `org.apache.log4j.Logger` — logging in BeanShell rules

### APIs
- **SCIM API**: REST API for identity management (IIQ 8.x+)
- **Plugin REST API**: Custom REST endpoints via IIQ plugins
- **Web Services**: SOAP-based legacy integration

### Key Concepts
- **Aggregation**: Process of reading accounts/entitlements from target systems
- **Provisioning**: Process of creating/modifying/disabling accounts on target systems
- **Certification**: Access review campaigns for compliance
- **Lifecycle Events**: Joiner, Mover, Leaver identity lifecycle triggers
- **SOD Policy**: Segregation of Duties — prevents conflicting access
"""

ISC_KNOWLEDGE = """
## SailPoint Identity Security Cloud (ISC) / IdentityNow (IDN) — Cloud

### Core Concepts
- **Identity**: Cloud identity object with attributes and access
- **Source**: Cloud connector configuration (equivalent to IIQ Application)
- **Access Profile**: Bundle of entitlements from a single source
- **Role**: Collection of access profiles, can span multiple sources
- **Entitlement**: Permission on a target source

### APIs
- **V3 API**: Primary REST API — `/v3/identities`, `/v3/access-profiles`, `/v3/roles`, etc.
- **v2025 API**: Next-generation API endpoints
- **Search API**: Elasticsearch-based search across identities, access, events
- **Transforms**: JSON-based data transformation rules (no code)
- **Event Triggers**: Webhook-based event system for automation

### Cloud Rules
- **Cloud Rules**: Java/BeanShell code that runs in ISC's sandboxed environment
- **Rule Types**: IdentityAttribute, CorrelationRule, ManagerCorrelation, BeforeProvisioning,
  AfterProvisioning, BuildMap, JDBCBuildMap, WebServiceBeforeOperation, WebServiceAfterOperation
- **Sandbox Constraints**: Limited library access, no filesystem, no network calls

### Connectors
- **SaaS Connectors**: TypeScript-based custom connectors using SailPoint connector SDK
- **Virtual Appliance (VA)**: On-premise gateway for connecting to behind-firewall systems
- **CCG**: Cloud Connector Gateway — manages VA connectivity

### Key Concepts
- **Identity Profiles**: Map source attributes to identity attributes
- **Lifecycle States**: Active, Inactive, etc. — control identity access
- **Transforms**: No-code data transformations (concatenation, substring, lookup, etc.)
- **Workflows**: No-code/low-code automation (trigger → action chains)
- **Governance Groups**: Groups of users for certification and governance
"""

IAM_KNOWLEDGE = """
## Identity and Access Management (IAM) Concepts

### Access Control Models
- **RBAC**: Role-Based Access Control — access via role membership
- **ABAC**: Attribute-Based Access Control — access via attribute-based policies
- **PBAC**: Policy-Based Access Control — centralized policy engine

### Compliance & Governance
- **SOD**: Segregation of Duties — prevent conflicting access combinations
- **JML**: Joiner-Mover-Leaver — identity lifecycle management
- **Access Certification**: Periodic review of access by managers/owners
- **Audit Trail**: Complete record of access changes for compliance

### Regulatory Frameworks
- **SOX**: Sarbanes-Oxley — financial controls, access review requirements
- **HIPAA**: Healthcare data privacy — minimum necessary access
- **GDPR**: EU data protection — right to access, right to erasure
- **PCI-DSS**: Payment card data security — strict access controls

### Architecture Patterns
- **Hub-and-Spoke**: Central IGA platform connecting to target systems
- **Zero Trust**: Never trust, always verify — continuous authentication
- **Least Privilege**: Minimum access necessary for job function
- **Just-in-Time (JIT)**: Temporary elevated access with automatic revocation
"""

# Combined knowledge for prompt augmentation
SAILPOINT_DOMAIN_KNOWLEDGE = f"""
{IIQ_KNOWLEDGE}

{ISC_KNOWLEDGE}

{IAM_KNOWLEDGE}
"""
