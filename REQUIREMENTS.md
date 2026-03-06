# SailPoint Query AI Agent — Requirements Specification

**Version:** 1.0
**Date:** 2026-03-05
**Status:** Draft

---

## 1. Project Overview

### 1.1 Purpose

The **SailPoint Query AI Agent** is an intelligent assistant that answers questions about SailPoint identity governance products — **IdentityIQ (IIQ)**, **IdentityNow (IDN)**, and **Identity Security Cloud (ISC)**. It leverages web search, official documentation, and community resources to deliver accurate, well-framed responses with source citations.

### 1.2 Scope

- Interactive CLI and web-based UI for querying SailPoint topics
- Real-time web search across SailPoint documentation and IAM resources
- Code generation, test case creation, and technical design capabilities
- Multi-agent architecture with **multi-specialized agents** — each agent is a full SailPoint and IAM domain expert capable of problem solving, explaining, coding, design, test creation, HLD, LLD, and advisory tasks
- ReAct (Reasoning + Acting) pattern for transparent, step-by-step problem solving
- Support for multiple LLM backends (Claude, OpenAI, GLM, and others)

### 1.3 Target Users

| User Role | Use Case |
|-----------|----------|
| **IAM Engineers** | Implementation guidance, troubleshooting, configuration help |
| **SailPoint Developers** | BeanShell rules, workflow design, API integration, connector development |
| **Security Architects** | Technical design reviews, architecture recommendations, compliance patterns |
| **QA Engineers** | Test case generation for SailPoint implementations |
| **Consultants** | Rapid knowledge lookup, client deliverable drafting |

---

## 2. Functional Requirements

### FR-1: Command-Line Interface (CLI)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Single-query mode: `sailpoint-agent query "<question>"` | Must |
| FR-1.2 | Interactive REPL mode: `sailpoint-agent chat` with conversation history | Must |
| FR-1.3 | Rich markdown rendering in terminal (headings, tables, code blocks) | Must |
| FR-1.4 | Syntax-highlighted code output for BeanShell, Java, XML, JSON, PowerShell | Must |
| FR-1.5 | Model selection flag: `--model <provider/model>` | Must |
| FR-1.6 | Verbose mode: `--verbose` to display ReAct reasoning traces | Should |
| FR-1.7 | Output export: `--output <file>` to save responses to file | Should |
| FR-1.8 | Session persistence: resume previous conversations | Could |

### FR-2: Web User Interface (UI)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Streamlit-based chat interface with message history | Must |
| FR-2.2 | Model selector in sidebar (Claude, OpenAI, GLM, etc.) | Must |
| FR-2.3 | Code blocks with syntax highlighting and copy buttons | Must |
| FR-2.4 | Expandable "Reasoning Trace" panels showing agent thought process | Should |
| FR-2.5 | Source citation links displayed below each response | Must |
| FR-2.6 | Configuration panel (temperature, max iterations, search depth) | Should |
| FR-2.7 | Conversation export (Markdown, PDF) | Could |

### FR-3: Web Search & Knowledge Retrieval

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Search across SailPoint official documentation domains | Must |
| FR-3.2 | Search SailPoint Developer Community forums | Must |
| FR-3.3 | Search SailPoint Compass Community knowledge base | Must |
| FR-3.4 | Search SailPoint open-source GitHub repositories | Should |
| FR-3.5 | Fetch and parse documentation pages for detailed content | Must |
| FR-3.6 | Return source URLs as citations with every response | Must |
| FR-3.7 | Fallback to broader IAM/identity governance resources when SailPoint docs are insufficient | Should |
| FR-3.8 | Domain-scoped search (prioritize SailPoint sources over general web) | Must |

**Target Knowledge Sources:**

| Source | URL | Content |
|--------|-----|---------|
| SailPoint Developer Portal | `developer.sailpoint.com` | APIs, SDKs, tools, extensibility |
| SailPoint Product Docs | `documentation.sailpoint.com` | Product guides, admin manuals |
| SailPoint Community | `community.sailpoint.com` | Forums, tutorials, knowledge base |
| SailPoint Developer Forums | `developer.sailpoint.com/discuss` | Developer Q&A, code samples |
| SailPoint OSS GitHub | `github.com/sailpoint-oss` | Open-source projects, examples |

### FR-4: SailPoint Domain Expertise

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Answer IdentityIQ (IIQ) questions: Rules, Workflows, TaskDefinitions, Certifications, Connectors, BeanShell scripting, SCIM APIs, Application onboarding | Must |
| FR-4.2 | Answer IdentityNow/ISC questions: V3 APIs, Transforms, Cloud Rules, Sources, Identity Profiles, Access Profiles, Roles, SaaS Connectors, Event Triggers | Must |
| FR-4.3 | Answer general IAM concepts: RBAC, ABAC, SOD, Provisioning, Certification campaigns, Access Requests, Lifecycle management | Must |
| FR-4.4 | Provide version-specific guidance (IIQ 7.x, 8.x; ISC current) | Should |
| FR-4.5 | Explain SailPoint API authentication (OAuth 2.0, Personal Access Tokens, Basic Auth) | Must |

### FR-5: Code Generation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Generate BeanShell scripts for IIQ Rules (Identity, Correlation, Creation, BuildMap, etc.) | Must |
| FR-5.2 | Generate Java code for custom IIQ connectors and plugins | Must |
| FR-5.3 | Generate REST API call examples (curl, Python requests, Postman collections) | Must |
| FR-5.4 | Generate XML configuration snippets (Application definitions, Workflow XML, TaskDefinition XML) | Must |
| FR-5.5 | Generate PowerShell scripts for Active Directory provisioning operations | Should |
| FR-5.6 | Generate ISC Transform JSON configurations | Must |
| FR-5.7 | Generate ISC Cloud Rule code (Java/BeanShell) | Must |
| FR-5.8 | Include inline comments and documentation in generated code | Must |

### FR-6: Test Case Generation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Generate unit test cases for BeanShell rules and Java components | Must |
| FR-6.2 | Generate integration test scenarios for connector operations | Must |
| FR-6.3 | Generate UAT (User Acceptance Testing) test cases for identity lifecycle flows | Must |
| FR-6.4 | Generate certification campaign test scenarios | Should |
| FR-6.5 | Generate access request workflow test cases | Should |
| FR-6.6 | Output test cases in structured format (ID, Description, Preconditions, Steps, Expected Result) | Must |
| FR-6.7 | Support test case generation for SOD policy validation | Should |

### FR-7: Technical Design Generation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1 | Generate High-Level Design (HLD) documents for SailPoint implementations | Must |
| FR-7.2 | Generate Low-Level Design (LLD) documents with technical specifications | Must |
| FR-7.3 | Generate data flow diagrams (text-based / ASCII) | Should |
| FR-7.4 | Generate architecture recommendations based on requirements | Must |
| FR-7.5 | Generate connector design specifications | Should |
| FR-7.6 | Generate workflow/business process design documents | Should |
| FR-7.7 | Include integration architecture for connected systems (AD, LDAP, HR systems, databases) | Should |

### FR-8: ReAct Agent Pattern

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.1 | Implement Reasoning + Acting loop: Think → Act → Observe → Repeat/Answer | Must |
| FR-8.2 | Display reasoning traces to users when requested (verbose/trace mode) | Must |
| FR-8.3 | Support multi-step research: chain multiple searches to build comprehensive answers | Must |
| FR-8.4 | Configurable maximum iteration limit (default: 5) | Must |
| FR-8.5 | Early termination when sufficient confidence is reached | Should |
| FR-8.6 | Multi-agent orchestration: coordinate multi-specialized agents, each capable of the full range of SailPoint and IAM tasks | Must |

### FR-8A: Multi-Specialized Agent Capabilities

Each agent in the system is a **multi-specialized SailPoint and IAM domain expert** — not a narrow single-task worker. Every agent must be capable of performing **all** of the following tasks:

| ID | Capability | Description | Priority |
|----|-----------|-------------|----------|
| FR-8A.1 | **Problem Solving & Troubleshooting** | Diagnose SailPoint configuration issues, debug BeanShell rules, resolve provisioning failures, analyze aggregation errors, troubleshoot connector problems | Must |
| FR-8A.2 | **Explaining & Teaching** | Clearly explain SailPoint concepts, IAM principles, product architectures, API behaviors, and workflow logic to users of all experience levels | Must |
| FR-8A.3 | **Code Generation** | Generate BeanShell rules, Java classes, XML configs, REST API examples, PowerShell scripts, ISC Transforms, Cloud Rules, SaaS connector code | Must |
| FR-8A.4 | **Test Case Creation** | Produce unit tests, integration tests, UAT scenarios, E2E test plans, SOD validation tests, certification campaign tests, and regression test suites | Must |
| FR-8A.5 | **High-Level Design (HLD)** | Create architecture-level design documents covering system topology, integration patterns, data flows, deployment strategy, and security architecture | Must |
| FR-8A.6 | **Low-Level Design (LLD)** | Create implementation-level design documents with detailed class/module designs, configuration specs, API contracts, data models, and error handling strategies | Must |
| FR-8A.7 | **Technical Design Documents** | Generate connector design specs, workflow/business process designs, provisioning plan designs, certification campaign designs, and integration architecture docs | Must |
| FR-8A.8 | **IAM Domain Expertise** | Serve as an identity and access management specialist covering RBAC, ABAC, SOD, JML lifecycle, access certifications, provisioning patterns, compliance frameworks, and zero-trust architecture | Must |
| FR-8A.9 | **SailPoint Product Expertise** | Deep knowledge across both IIQ (on-prem) and ISC/IDN (cloud), including version-specific guidance, migration strategies, best practices, and anti-patterns | Must |
| FR-8A.10 | **Advisory & Best Practices** | Recommend architecture patterns, implementation approaches, performance optimizations, security hardening, and operational procedures for SailPoint deployments | Should |

> **Design Principle:** The orchestrator routes queries to agents not because they have narrow specializations, but to enable parallel processing, context isolation, and workload distribution. Any agent can handle any SailPoint/IAM task.

### FR-8B: Skills System

Agents use a **Skills system** (filesystem-based `.claude/skills/*.md` files) that provides structured instructions, templates, and domain knowledge for specific task types. Skills are automatically invoked by agents when relevant.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8B.1 | Skills defined as markdown files in `.claude/skills/` directory | Must |
| FR-8B.2 | Each Skill provides structured instructions, response templates, and domain knowledge for a specific task type | Must |
| FR-8B.3 | Agents autonomously invoke relevant Skills based on query classification | Must |
| FR-8B.4 | Multiple Skills can be chained within a single agent interaction | Should |
| FR-8B.5 | Skills extensible — new Skills added by creating new `.md` files without code changes | Must |
| FR-8B.6 | Built-in Skills for: research, code generation, test case creation, HLD, LLD, troubleshooting, IAM advisory, technical design | Must |

**Skill Files:**

| Skill | File | Trigger |
|-------|------|---------|
| SailPoint Research | `sailpoint-research.md` | Questions about features, concepts, configurations |
| Code Generation | `code-generation.md` | Requests for BeanShell, Java, XML, REST, PowerShell code |
| Test Case Creation | `test-case-creation.md` | Requests for test cases, test scenarios, test plans |
| HLD Design | `hld-design.md` | Requests for high-level architecture design |
| LLD Design | `lld-design.md` | Requests for low-level implementation design |
| Troubleshooting | `troubleshooting.md` | Debug, diagnose, fix, resolve SailPoint issues |
| IAM Advisory | `iam-advisory.md` | IAM strategy, compliance, RBAC, SOD, zero-trust |
| Technical Design | `technical-design.md` | Connector, workflow, provisioning, integration designs |

### FR-9: Multi-LLM Support

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-9.1 | Support Claude models (Opus, Sonnet, Haiku) as default LLM | Must |
| FR-9.2 | Support OpenAI models (GPT-4, GPT-4o, etc.) | Must |
| FR-9.3 | Support GLM models (GLM-4, etc.) | Should |
| FR-9.4 | Support any model available through LiteLLM (100+ models) | Should |
| FR-9.5 | Runtime model switching via CLI flag or UI selector | Must |
| FR-9.6 | Per-model configuration (temperature, max tokens, API keys) | Must |
| FR-9.7 | Automatic fallback to secondary model on primary failure | Should |

### FR-10: Response Quality

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10.1 | Responses must be well-structured with clear headings and sections | Must |
| FR-10.2 | Include source citations with clickable URLs | Must |
| FR-10.3 | Code blocks must use correct syntax highlighting per language | Must |
| FR-10.4 | Explanations should be clear, concise, and accessible to mid-level engineers | Must |
| FR-10.5 | Responses should distinguish between IIQ and IDN/ISC when relevant | Must |
| FR-10.6 | Flag deprecated APIs or features when referenced | Should |
| FR-10.7 | Provide confidence indicators for answers | Should |

---

## 3. Non-Functional Requirements

### NFR-1: Accuracy

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | Response accuracy relative to official SailPoint documentation | ≥ 99% similarity |
| NFR-1.2 | Code generation correctness (compilable/runnable without errors) | ≥ 95% |
| NFR-1.3 | API endpoint accuracy (correct URLs, methods, parameters) | ≥ 99% |

### NFR-2: Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-2.1 | Simple query response time (no web search needed) | < 10 seconds |
| NFR-2.2 | Standard query response time (1-2 web searches) | < 30 seconds |
| NFR-2.3 | Complex research query response time (multi-step search) | < 60 seconds |
| NFR-2.4 | UI page load time | < 3 seconds |

### NFR-3: Extensibility

| ID | Requirement |
|----|-------------|
| NFR-3.1 | Plugin architecture for adding new LLM providers without core changes |
| NFR-3.2 | Tool system allowing new tools to be registered dynamically |
| NFR-3.3 | Prompt templates externalized for easy customization |
| NFR-3.4 | Agent types extensible — new specialist agents can be added |

### NFR-4: Configuration

| ID | Requirement |
|----|-------------|
| NFR-4.1 | Environment variables via `.env` file for secrets (API keys) |
| NFR-4.2 | Application config via `config.yaml` for non-secret settings |
| NFR-4.3 | CLI flags override config file values |
| NFR-4.4 | Sensible defaults for all configuration options |

### NFR-5: Observability

| ID | Requirement |
|----|-------------|
| NFR-5.1 | Structured logging (JSON format) with configurable log levels |
| NFR-5.2 | Token usage tracking per request (prompt tokens, completion tokens, cost) |
| NFR-5.3 | Request/response latency metrics |
| NFR-5.4 | Agent reasoning trace logging for debugging |

### NFR-6: Reliability

| ID | Requirement |
|----|-------------|
| NFR-6.1 | Graceful error handling — never crash on bad input |
| NFR-6.2 | LLM provider failover — automatic fallback on API errors |
| NFR-6.3 | Rate limiting awareness — respect API rate limits with backoff |
| NFR-6.4 | Timeout handling for web searches and LLM calls |

---

## 4. Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11+ | Core implementation language |
| Agent Framework | Claude Agent SDK (`claude_agent_sdk`) | Agentic ReAct loop, tool execution, subagent orchestration (Task), Skills, MCP server support |
| Multi-LLM Gateway | LiteLLM | Unified API for 100+ LLM models |
| CLI Framework | Click + Rich | Command-line interface with rich output |
| Web UI | Streamlit | Web-based chat interface |
| Web Search | WebSearch / WebFetch (Claude Agent SDK tools) | Real-time web search |
| Configuration | python-dotenv + PyYAML | Environment and app configuration |
| HTTP Client | httpx | Async HTTP requests for API calls |
| Testing | pytest + pytest-asyncio | Unit and integration testing |
| Logging | structlog | Structured logging |
| Packaging | pyproject.toml + pip | Python package management |

---

## 5. Constraints & Assumptions

### Constraints
- LLM API keys must be provided by the user (not bundled)
- Web search quality depends on SailPoint documentation availability and indexing
- Token costs are borne by the user based on their LLM provider pricing
- Offline mode is not supported (requires internet for web search and LLM APIs)

### Assumptions
- Users have Python 3.11+ installed
- Users have valid API keys for at least one supported LLM provider
- SailPoint documentation websites remain publicly accessible
- Users have basic familiarity with SailPoint products and IAM concepts

---

## 6. Glossary

| Term | Definition |
|------|------------|
| **IIQ** | SailPoint IdentityIQ — on-premise identity governance platform |
| **IDN** | SailPoint IdentityNow — cloud-based identity platform (now ISC) |
| **ISC** | SailPoint Identity Security Cloud — rebranded IdentityNow |
| **ReAct** | Reasoning + Acting — agent pattern that interleaves thinking and tool use |
| **BeanShell** | Java-based scripting language used in IdentityIQ rules |
| **SCIM** | System for Cross-domain Identity Management — REST API standard |
| **SOD** | Segregation of Duties — compliance control preventing conflicting access |
| **HLD** | High-Level Design — architecture-level technical document |
| **LLD** | Low-Level Design — implementation-level technical document |
| **LLM** | Large Language Model — AI model used as the agent's reasoning engine |
