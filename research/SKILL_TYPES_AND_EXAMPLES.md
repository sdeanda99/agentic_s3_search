# Claude Skills: Types and Examples

## Overview

The knowledge-work-plugins repository contains **53 documented skills** across **11 plugins** and **major business functions**. This guide maps skill types, their purposes, and concrete examples.

---

## 1. LEGAL & COMPLIANCE SKILLS

### Contract Analysis Skills
**Purpose:** Analyze contracts systematically against organizational standards

#### contract-review
- **Use when:** Reviewing vendor contracts, customer agreements, commercial terms
- **How it works:** Loads org playbook, analyzes 8+ clause types, flags deviations (GREEN/YELLOW/RED), generates redlines
- **Key components:**
  - Playbook-based methodology (org's standard positions)
  - Clause-by-clause analysis (limitation of liability, indemnification, IP, data protection, etc.)
  - Deviation classification (acceptable/negotiate/escalate)
  - Redline generation with fallback positions
  - Negotiation priority framework (must-haves/should-haves/nice-to-haves)
- **Example output:** Contract review with flagged clauses, specific redline language, business impact assessment

#### nda-triage
- **Use when:** New NDAs arrive, assessing NDA risk, routing NDAs for review
- **How it works:** Systematic 10-point evaluation, GREEN/YELLOW/RED classification, routing recommendations
- **Key components:**
  - Agreement structure verification
  - Confidential information scope review
  - Standard carveouts check (public knowledge, independent development, etc.)
  - Problematic provisions detection (non-compete, non-solicitation, exclusivity)
  - Classification rules and routing
- **Example output:** NDA screening with specific issues flagged and next steps

### Compliance & Privacy Skills
**Purpose:** Navigate regulations and data protection requirements

#### compliance
- **Use when:** Reviewing DPAs, handling data subject requests, assessing privacy regulations
- **How it works:** Covers GDPR, CCPA, LGPD, POPIA, UK GDPR, and other frameworks
- **Key components:**
  - Privacy regulation overview (GDPR, CCPA, LGPD, etc.)
  - DPA review checklist (100+ items)
  - Data subject request intake and response process
  - International transfer requirements (SCCs, adequacy decisions)
  - Regulatory monitoring and escalation criteria
- **Example output:** DPA review with compliance gaps, data subject request response template

### Response & Template Skills
**Purpose:** Generate templated legal communications

#### canned-responses
- **Use when:** Responding to routine legal inquiries, generating DSR responses, discovery holds
- **How it works:** Manages templates for common inquiries with smart escalation detection
- **Key components:**
  - Template management methodology
  - Response categories (DSR, discovery holds, privacy inquiries, vendor questions, NDAs, subpoenas)
  - Customization guidelines (names, dates, jurisdiction-specific adjustments)
  - Escalation trigger detection (when NOT to use templates)
  - Template format with variables
- **Example output:** Templated response with variable substitution, escalation detection

---

## 2. SALES & OUTREACH SKILLS

### Prospect Research & Outreach
**Purpose:** Research prospects and draft personalized outreach

#### draft-outreach
- **Use when:** Drafting cold emails, writing LinkedIn outreach, researching prospects
- **How it works:** Research-first approach (web search + enrichment + CRM), then draft personalized message
- **Key components:**
  - Research execution (web search, enrichment data, CRM history)
  - Hook identification (trigger events, mutual connections, content, company initiatives)
  - AIDA email structure (attention/interest/desire/action)
  - Channel selection (email preferred, LinkedIn fallback)
  - Follow-up sequence templates
  - Style guidelines (plain text, no markdown, short paragraphs)
- **Example output:** Personalized email draft with subject line alternatives, LinkedIn connection request, follow-up sequence

#### account-research
- **Use when:** Deep-dive research on target accounts, buying committee analysis
- **How it works:** Research account strategy, buying committee composition, decision-making dynamics
- **Key components:**
  - Account profiling methodology
  - Buying committee identification
  - Pain point mapping
  - Competitive landscape analysis (within their industry)
  - Deal sizing and timeline assessment
- **Example output:** Account research summary with buying committee names, pain points, deal opportunity assessment

### Call & Activity Management
**Purpose:** Prepare for calls and synthesize call outcomes

#### call-prep
- **Use when:** Preparing for discovery calls, demos, negotiations
- **How it works:** Gathers context from CRM, company research, prior interactions
- **Key components:**
  - Discovery call methodology
  - Context gathering (account research, prior interactions, competition)
  - Objection handling framework
  - Discovery question templates
  - Call outcome structure (next steps, action items, timeline)
- **Example output:** Call prep document with discovery questions, objection handling strategies, next steps

---

## 3. FINANCE & ACCOUNTING SKILLS

### Transaction & Reconciliation
**Purpose:** Prepare journal entries and reconcile accounts

#### journal-entry-prep
- **Use when:** Preparing month-end accruals, depreciation, revenue entries
- **How it works:** Generates entries with supporting documentation and review workflows
- **Key components:**
  - Accrual types (AP accruals, revenue recognition, prepaids, payroll, depreciation)
  - Supporting documentation requirements
  - Debit/credit verification
  - Review workflows and sign-off procedures
  - Common mistakes to avoid
- **Example output:** Formatted journal entry with supporting detail, account codes, explanations

#### reconciliation
- **Use when:** Reconciling GL to subledger, bank reconciliation, intercompany
- **How it works:** Systematically identifies and categorizes reconciling items
- **Key components:**
  - Reconciliation methodology (GL vs. subledger vs. bank vs. intercompany)
  - Reconciling item categorization
  - Aging analysis
  - Exception identification and resolution
- **Example output:** Reconciliation schedule with reconciling items identified and explained

### Reporting & Analysis
**Purpose:** Generate financial reports and analyze variances

#### financial-statements
- **Use when:** Generating P&L, balance sheet, cash flow statements
- **How it works:** Produces GAAP-compliant statements with flux analysis
- **Key components:**
  - Income statement format and GAAP presentation
  - Balance sheet structure
  - Cash flow statement
  - Period-over-period comparison
  - Variance analysis and flux methodology
- **Example output:** Formatted financial statements with comparative periods and variance analysis

#### variance-analysis
- **Use when:** Investigating budget variances, explaining P&L changes quarter-over-quarter
- **How it works:** Decomposes variances into drivers with narrative explanations
- **Key components:**
  - Variance decomposition techniques (price/volume, rate/mix, etc.)
  - Materiality assessment
  - Waterfall analysis
  - Narrative generation for unexplained variances
  - Trending and pattern analysis
- **Example output:** Variance analysis with decomposition, waterfall chart, narrative explanations

---

## 4. DATA & ANALYTICS SKILLS

### Query & Analysis
**Purpose:** Generate and explain data queries, perform statistical analysis

#### sql-queries
- **Use when:** Translating business questions to SQL, optimizing queries
- **How it works:** Generates SQL from natural language with appropriate database dialect
- **Key components:**
  - Query type detection (aggregation, filtering, joining, time series, etc.)
  - SQL dialect support (BigQuery, Snowflake, PostgreSQL, Databricks)
  - Query optimization suggestions
  - Explanation of query logic
  - Common patterns and query templates
- **Example output:** SQL query with explanation, performance considerations, sample results

#### statistical-analysis
- **Use when:** Hypothesis testing, confidence intervals, regression analysis
- **How it works:** Guides statistical methodology and interpretation
- **Key components:**
  - Hypothesis testing framework
  - Statistical test selection
  - Confidence interval calculation
  - Regression analysis (linear, logistic)
  - P-value and significance interpretation
  - Common statistical pitfalls to avoid
- **Example output:** Analysis results with statistical significance assessment, confidence intervals

### Data Quality & Context
**Purpose:** Validate data quality and bootstrap company-specific analysis

#### data-context-extractor (Meta-skill)
- **Use when:** Creating company-specific data analysis skills from scratch
- **How it works:** Two modes: Bootstrap (create skill from DB discovery) and Iteration (add domain context)
- **Key components:**
  - Database discovery (schema exploration)
  - Entity disambiguation (what "user" and "customer" mean in this company)
  - Metric extraction (how each KPI is calculated)
  - Data quality gotchas identification
  - Reference file generation (entities.md, metrics.md, table docs, etc.)
- **Example output:** Complete data analysis skill with reference materials for the company's specific warehouse

#### data-validation
- **Use when:** Data quality checks, anomaly detection, completeness assessment
- **How it works:** Systematic validation rules and threshold detection
- **Key components:**
  - Null/missing value detection
  - Outlier identification
  - Data type validation
  - Referential integrity checks
  - Trend and seasonality anomalies
- **Example output:** Data quality report with issues flagged, severity assessment, remediation steps

---

## 5. CUSTOMER SUPPORT SKILLS

### Ticket & Response Management
**Purpose:** Triage tickets and draft responses

#### ticket-triage
- **Use when:** Incoming support tickets, categorizing and routing
- **How it works:** Applies triage rules, categorizes severity, routes to appropriate team
- **Key components:**
  - Ticket classification (issue type, severity, urgency)
  - Routing logic (which team/person)
  - SLA determination
  - Priority scoring
- **Example output:** Triaged ticket with category, severity, suggested routing, SLA

#### response-drafting
- **Use when:** Drafting customer-facing responses to support tickets
- **How it works:** Generates empathetic, helpful, solution-focused responses
- **Key components:**
  - Response structure (acknowledge, explain, solutions, next steps)
  - Tone guidelines (empathetic but professional)
  - Common solutions and workarounds
  - Escalation decision logic
- **Example output:** Draft response with tone-appropriate language, solution steps, follow-up plan

### Knowledge Management
**Purpose:** Create and maintain knowledge base articles

#### knowledge-management
- **Use when:** Converting resolved tickets to KB articles, creating how-to guides
- **How it works:** Structures articles for searchability and customer self-service
- **Key components:**
  - Article types (how-to, troubleshooting, FAQ, known issues)
  - Formatting standards (headers, lists, code blocks, callouts)
  - Searchability optimization (titles, keywords, customer language)
  - Article lifecycle (draft, published, needs update, archived, retired)
  - Content linking strategy
  - Maintenance cadence and stale content detection
- **Example output:** Well-structured KB article with proper titles, steps, related links, metadata

---

## 6. MARKETING & BRAND SKILLS

### Brand & Voice Enforcement
**Purpose:** Maintain consistent brand voice and messaging

#### brand-voice
- **Use when:** Reviewing content for brand consistency, documenting brand voice
- **How it works:** Provides brand voice framework, style enforcement, terminology management
- **Key components:**
  - Brand personality definition (if it were a person, would be...)
  - Voice attributes (formality, authority, emotion, complexity, energy, humor, innovation)
  - Tone adaptation by channel and situation
  - Grammar and mechanics rules (Oxford comma, contractions, em dashes, numbers, etc.)
  - Style conventions (headings, bold, italics, lists, links, callouts)
  - Terminology management (preferred terms, product names, inclusive language, jargon)
- **Example output:** Content review with voice/tone feedback, terminology corrections, style improvements

#### content-creation
- **Use when:** Drafting blog posts, marketing copy, email campaigns
- **How it works:** Generates content following brand voice and targeting specific audiences
- **Key components:**
  - Audience analysis and segmentation
  - Content format selection (blog, email, social, whitepaper, etc.)
  - Headline and hook development
  - Copy structure and messaging
  - CTA optimization
- **Example output:** Drafted content piece with brand voice applied, multiple headline options

---

## 7. PRODUCT MANAGEMENT SKILLS

### Strategy & Planning
**Purpose:** Define product roadmap and strategy

#### feature-spec
- **Use when:** Writing feature specifications, defining requirements
- **How it works:** Generates structured feature specs with user stories, acceptance criteria, design considerations
- **Key components:**
  - Feature overview and value proposition
  - User stories and use cases
  - Acceptance criteria
  - Design considerations
  - Edge cases and constraints
  - Success metrics
- **Example output:** Feature specification document with all planning artifacts

#### roadmap-management
- **Use when:** Planning product roadmap, sequencing initiatives
- **How it works:** Structures roadmap planning with prioritization frameworks
- **Key components:**
  - Roadmap structure (themes, quarters, initiatives)
  - Prioritization methodology (impact/effort, MoSCoW, weighted scoring)
  - Sequencing logic (dependencies, learning sequencing)
  - Stakeholder communication planning
- **Example output:** Product roadmap with prioritized initiatives, dependencies, timeline

### Research & Analytics
**Purpose:** Synthesize user research and track metrics

#### user-research-synthesis
- **Use when:** Analyzing user research, identifying patterns, extracting insights
- **How it works:** Structures qualitative research findings into actionable insights
- **Key components:**
  - Research aggregation (interviews, surveys, usability tests, support tickets)
  - Pattern identification and theming
  - User need prioritization
  - Insight documentation and sharing
- **Example output:** Research summary with themes, user needs, ranked by importance

#### metrics-tracking
- **Use when:** Defining success metrics, tracking product health
- **How it works:** Guides metric definition and interpretation
- **Key components:**
  - Metric definition (leading vs. lagging, activation, engagement, retention)
  - Targets and thresholds
  - Tracking and monitoring setup
  - Interpretation and action frameworks
- **Example output:** Metric dashboard definition with KPIs, targets, monitoring approach

---

## 8. ENTERPRISE SEARCH SKILLS

### Search Orchestration
**Purpose:** Search across multiple sources and synthesize results

#### search-strategy
- **Use when:** Searching for information across company systems
- **How it works:** Decomposes questions into source-specific searches, ranks and synthesizes results
- **Key components:**
  - Query type classification (decision, status, document, person, factual, temporal, exploratory)
  - Search component extraction (keywords, entities, intent signals, constraints)
  - Source-specific query translation (Slack syntax, Wiki search, task tracker syntax)
  - Result ranking and relevance scoring
  - Ambiguity handling and clarifying questions
  - Fallback strategies for unavailable sources
  - Parallel execution and deduplication
- **Example output:** Search results from multiple sources, ranked by relevance, synthesized into coherent answer

#### knowledge-synthesis
- **Use when:** Answering broad questions requiring information synthesis
- **How it works:** Gathers information from multiple sources and synthesizes into coherent answer
- **Key components:**
  - Source evaluation and authority assessment
  - Information extraction and organization
  - Synthesis and narrative generation
  - Confidence and certainty communication
- **Example output:** Synthesized answer drawing from multiple sources with citations

---

## 9. ENTERPRISE & PRODUCTIVITY SKILLS

### Task & Calendar Management
**Purpose:** Manage workflows, tasks, and calendar

#### task-management
- **Use when:** Creating tasks, managing task lists, tracking work
- **How it works:** Helps structure task management with clarity and tracking
- **Key components:**
  - Task definition (description, acceptance criteria)
  - Priority and sequencing
  - Dependencies and blocking relationships
  - Assignment and ownership
  - Status tracking and updates
- **Example output:** Well-structured task with all planning details

#### meeting-briefing
- **Use when:** Preparing for meetings, creating meeting agendas
- **How it works:** Gathers context, creates focused agendas, surfaces key decisions
- **Key components:**
  - Meeting purpose clarity
  - Agenda structure (topics, time allocation, decisions needed)
  - Context gathering (prior discussions, relevant data, stakeholder needs)
  - Decision frameworks
- **Example output:** Meeting prep document with focused agenda, context, decision frameworks

---

## 10. SCIENTIFIC RESEARCH SKILLS

### Literature & Target Research
**Purpose:** Literature search and research synthesis

#### literature-search
- **Use when:** Finding relevant papers, systematic reviews, research synthesis
- **How it works:** Searches literature databases, organizes findings
- **Key components:**
  - Search strategy (keywords, boolean operators, databases)
  - Study identification and screening
  - Data extraction
  - Evidence synthesis
- **Example output:** Literature summary with key findings, evidence quality assessment

#### target-prioritization
- **Use when:** Selecting research targets, assessing tractability and impact
- **How it works:** Applies prioritization frameworks to target selection
- **Key components:**
  - Target characterization
  - Disease relevance assessment
  - Druggability evaluation
  - Market and feasibility analysis
- **Example output:** Target prioritization with scores and recommendation

---

## 11. PLUGIN MANAGEMENT SKILLS (Meta-Skills)

### Plugin Customization
**Purpose:** Customize plugins for specific organizations

#### cowork-plugin-customizer
- **Use when:** Customizing a plugin for organization's specific tools
- **How it works:** Finds customization points, gathers org context, replaces placeholders, connects MCP servers
- **Key components:**
  - Customization point identification (grep for ~~ placeholders)
  - Context gathering from company knowledge MCPs
  - Placeholder replacement
  - MCP server discovery and connection
  - .plugin file packaging
- **Example output:** Customized plugin ready for team distribution

#### cowork-plugin-creator
- **Use when:** Creating a new plugin for custom workflow
- **How it works:** Guides through plugin creation process
- **Key components:**
  - Plugin structure and organization
  - Skill creation
  - Command definition
  - MCP configuration
  - Testing and refinement
- **Example output:** New plugin ready for use

---

## Skill Composition Patterns

### Single Skill Usage
A user asks, Claude applies one skill:
```
User: "Review this contract against our playbook"
→ Claude applies contract-review skill
```

### Multi-Skill Orchestration
A command uses multiple skills transparently:
```
User: "Draft outreach to Acme Corp"
→ draft-outreach skill internally uses research-prospect skill
→ Output: Personalized email with research summary
```

### Skill Layering
Complex tasks use multiple skills in sequence:
```
User: "Analyze why revenue is down 15% vs. last quarter"
→ variance-analysis skill decomposes variance
→ statistical-analysis skill assesses significance
→ search-strategy skill finds context (market, pricing, competition)
→ Output: Comprehensive variance analysis with business context
```

---

## Finding the Right Skill

**By domain:**
- Legal: contract-review, nda-triage, compliance, legal-risk-assessment, canned-responses
- Sales: draft-outreach, call-prep, account-research, competitive-intelligence
- Finance: journal-entry-prep, reconciliation, financial-statements, variance-analysis
- Data: sql-queries, statistical-analysis, data-validation, data-context-extractor
- Support: ticket-triage, response-drafting, knowledge-management
- Marketing: brand-voice, content-creation, campaign-planning
- Product: feature-spec, roadmap-management, user-research-synthesis, metrics-tracking

**By task type:**
- Document analysis: contract-review, nda-triage, knowledge-management
- Research: account-research, literature-search, user-research-synthesis
- Template/response generation: canned-responses, response-drafting, content-creation
- Methodology/process: variance-analysis, reconciliation, statistical-analysis
- Framework/classification: legal-risk-assessment, ticket-triage, brand-voice

---

## Summary

Skills encode domain expertise as reusable, customizable Markdown files. Each skill provides:
- Procedural guidance (how to think about problems)
- Classification frameworks (how to categorize decisions)
- Best practices (common pitfalls, dos and don'ts)
- Templates and checklists (structured approaches)
- Examples (concrete demonstrations)

Skills work automatically when relevant, or can be invoked explicitly via commands. They compose seamlessly, allowing complex workflows to be built from simpler skill building blocks.

