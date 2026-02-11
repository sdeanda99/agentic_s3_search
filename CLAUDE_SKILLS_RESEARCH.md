# Claude Skills Research Summary
## Knowledge-Work-Plugins Repository Analysis

**Repository:** https://github.com/anthropics/knowledge-work-plugins
**Date:** February 10, 2026
**Scope:** 11 plugins, 53+ skills, comprehensive file-based architecture

---

## 1. CLAUDE SKILLS FORMAT & STRUCTURE

### 1.1 File Format
Skills are **YAML-frontmatter Markdown files** with the `.md` extension, specifically named `SKILL.md`.

**File Location Pattern:**
```
plugin-name/
├── skills/
│   └── skill-name/
│       └── SKILL.md
└── commands/
    └── command-name.md
```

### 1.2 Skill File Schema

Every skill file follows this structure:

```markdown
---
name: skill-identifier
description: One-sentence description of when to use this skill
---

# [Skill Title]

[Longer explanation of what the skill does]

## [Section 1]
[Content]

## [Section 2]
[Content]
```

**Frontmatter Fields:**
- `name` (required): Unique identifier for the skill (kebab-case)
- `description` (required): Brief, trigger-based description explaining when Claude should use this skill
- `compatibility` (optional): Special compatibility requirements

**Example:** Legal contract review skill
```yaml
---
name: contract-review
description: Review contracts against your organization's negotiation playbook, flagging deviations and generating redline suggestions. Use when reviewing vendor contracts, customer agreements, or any commercial agreement where you need clause-by-clause analysis against standard positions.
---
```

### 1.3 Core Skill Components

Skills consist of:

1. **Context & Expertise** — Domain knowledge encoded as procedural guidance
2. **Methodology Sections** — Step-by-step processes and frameworks
3. **Classification Frameworks** — How to categorize decisions (GREEN/YELLOW/RED)
4. **Template Formats** — Structured output patterns
5. **Checklists** — Systematic evaluation criteria
6. **Best Practices** — Industry standards and guidelines
7. **Examples** — Real-world application scenarios
8. **Edge Cases** — Gotchas and escalation triggers

**There is NO code.** Skills are pure instruction and knowledge documentation.

### 1.4 Typical Skill Structure (Example: Contract Review)

```
# Contract Review Skill

[Introduction]

## Playbook-Based Review Methodology
### Loading the Playbook
### Review Process
### Common Clause Analysis
  - Limitation of Liability
  - Indemnification
  - IP Ownership
  - Data Protection
  - [... more clause types]

## Deviation Severity Classification
### GREEN -- Acceptable
### YELLOW -- Negotiate
### RED -- Escalate

## Redline Generation Best Practices
[Specific formatting and prioritization guidance]

## Negotiation Priority Framework
### Tier 1 -- Must-Haves
### Tier 2 -- Should-Haves
### Tier 3 -- Nice-to-Haves
```

---

## 2. SKILL CATEGORIES & AVAILABLE SKILLS

The repository contains **11 plugins** across major business functions, each with **4-8 skills**.

### 2.1 Plugin Inventory

| Plugin | Domain | Skill Count | Primary Use Case |
|--------|--------|------------|------------------|
| **legal** | Legal/Compliance | 6 skills | Contract review, NDA triage, compliance, risk assessment, response templates |
| **sales** | Revenue/Outreach | 7 skills | Prospect research, call prep, outreach drafting, competitive intelligence |
| **customer-support** | Support Operations | 5 skills | Ticket triage, response drafting, escalation, KB management |
| **product-management** | Product Strategy | 6 skills | Feature specs, roadmap management, user research synthesis, metrics tracking |
| **marketing** | Content & Brand | 5 skills | Brand voice enforcement, content creation, campaign planning, competitive analysis |
| **finance** | Accounting/Close | 6 skills | Journal entry prep, reconciliation, financial statements, variance analysis |
| **data** | Analytics | 7 skills | SQL query generation, statistical analysis, data validation, visualization |
| **enterprise-search** | Knowledge Retrieval | 3 skills | Search strategy, knowledge synthesis, source management |
| **productivity** | Workflow Management | 5 skills | Task management, calendar coordination, meeting prep, context curation |
| **bio-research** | Scientific Research | 3 skills | Literature search, genomics analysis, target prioritization |
| **cowork-plugin-management** | Plugin Ecosystem | 2 skills | Plugin customization, plugin creation |

**Total: 53 skills documented**

### 2.2 Example Skills by Category

#### Legal Skills
1. **contract-review** — Playbook-based contract analysis with clause-by-clause review
2. **nda-triage** — NDA screening with GREEN/YELLOW/RED classification
3. **compliance** — Privacy regulations (GDPR, CCPA), DPA review, data subject requests
4. **legal-risk-assessment** — Risk severity framework and escalation criteria
5. **canned-responses** — Template management for common legal inquiries
6. **meeting-briefing** — Meeting prep methodology and context gathering

#### Sales Skills
1. **draft-outreach** — Research-first prospect outreach with personalization
2. **call-prep** — Discovery call preparation and research synthesis
3. **account-research** — Deep-dive research on accounts and buying committees
4. **competitive-intelligence** — Competitive landscape analysis and battlecards
5. **daily-briefing** — Sales activity briefing and pipeline review
6. **create-an-asset** — Sales collateral generation (one-pagers, case studies)

#### Finance Skills
1. **journal-entry-prep** — Accrual and entry generation with supporting documentation
2. **reconciliation** — GL-to-subledger, bank, and intercompany reconciliation
3. **financial-statements** — Income statement and balance sheet generation
4. **variance-analysis** — Variance decomposition and waterfall analysis
5. **close-management** — Month-end close checklist and task sequencing
6. **audit-support** — SOX testing and control assessment

#### Data Skills
1. **sql-queries** — SQL generation from natural language
2. **statistical-analysis** — Hypothesis testing, confidence intervals, regression
3. **data-validation** — Data quality checks and anomaly detection
4. **data-visualization** — Chart and dashboard recommendations
5. **data-exploration** — Exploratory data analysis methodology
6. **data-context-extractor** — Meta-skill for bootstrapping company-specific data analysis skills

#### Customer Support Skills
1. **knowledge-management** — KB article creation and maintenance
2. **ticket-triage** — Support ticket categorization and routing
3. **response-drafting** — Customer-facing response generation
4. **escalation** — Issue escalation workflow and severity assessment
5. **customer-research** — Customer context and history research

---

## 3. HOW SKILLS WORK (Integration Mechanism)

### 3.1 Skill Invocation Model

Skills are **not tools** — they are **behavioral instructions embedded in system prompts**.

When a plugin is loaded, Claude's system prompt is augmented with:
- All skill files from the `skills/` directory
- Their content becomes available context for Claude's reasoning

**Mechanism:**
1. User invokes a plugin: `claude plugin install sales@knowledge-work-plugins`
2. Claude's system prompt automatically includes all skills from that plugin
3. Claude detects when skill knowledge is relevant to the user's request
4. Claude applies the skill's methodology and frameworks to generate output
5. No explicit "tool calling" required

### 3.2 Skill Triggering

Skills activate **automatically based on relevance detection**, but can also be referenced explicitly.

**Example from draft-outreach skill description:**
```
Use when drafting personalized outreach, researching prospects, or writing cold emails.
Trigger with "draft outreach to [person/company]", "write cold email to [prospect]", "reach out to [name]".
```

**Three triggering mechanisms:**
1. **Explicit command** — `/skill-name` or mention of the skill
2. **Natural language trigger** — User mentions keywords/patterns that match skill description
3. **Context-aware activation** — Claude recognizes the current task requires the skill

### 3.3 Skill Composition & Interaction

**Skills do NOT stand alone** — they interact and reference each other:

**Example:** draft-outreach skill internally uses research-prospect skill
```markdown
## Execution Flow

### Step 2: Research First (Always)

**Use research-prospect skill internally:**
```
1. Web search for company + person
2. If Enrichment connected: Get verified contact info
3. If CRM connected: Check for prior relationship
```
```

This happens transparently to the user — the skill can orchestrate other skills.

---

## 4. SKILL COMPONENTS IN DETAIL

### 4.1 Instruction/Behavior Modification

Skills heavily emphasize **how Claude should think about a problem**, not just what output to produce.

**Example: NDA Triage Skill**
- Defines systematic evaluation criteria (10-point checklist)
- Teaches risk classification logic (GREEN/YELLOW/RED rules)
- Provides edge case handling guidance
- Includes common issues and redline approaches

**This is pure behavioral instruction** — no data structures, just guidance.

### 4.2 Domain Expertise Encoding

Skills encode **tribal knowledge** that would normally require hiring a specialist.

**Finance Example (journal-entry-prep skill):**
- Standard accrual types (AP accruals, revenue recognition, payroll)
- Supporting documentation requirements
- Review workflows and sign-off procedures
- Common mistakes and how to avoid them

**Legal Example (contract-review skill):**
- What constitutes each major clause type
- Market standard positions for each clause
- How to decompose liability protections
- Negotiation prioritization frameworks

### 4.3 Custom Tools Definition?

**No.** Skills do NOT define custom tools. Tools are defined separately in `.mcp.json` (MCP servers for external integrations).

**Key distinction:**
- **Skills** = domain expertise and methodology
- **Tools/Connectors** = integration with external systems (Slack, Box, Jira, etc.)
- **Commands** = explicit slash commands that users invoke

---

## 5. LEGAL SKILL DEEP-DIVE (Document Analysis Example)

The legal plugin is the most sophisticated in the repository. It demonstrates how skills handle complex document analysis.

### 5.1 Legal Plugin Structure

```
legal/
├── .claude-plugin/plugin.json
├── .mcp.json                    [Slack, Box, Egnyte, Atlassian, MS 365]
├── README.md
├── CONNECTORS.md
├── commands/
│   ├── review-contract.md       [Explicit command for contract review]
│   ├── triage-nda.md            [Explicit command for NDA triage]
│   ├── vendor-check.md
│   ├── brief.md
│   └── respond.md
└── skills/
    ├── contract-review/SKILL.md          [Comprehensive contract analysis]
    ├── nda-triage/SKILL.md               [NDA screening]
    ├── compliance/SKILL.md               [Privacy & regulation]
    ├── canned-responses/SKILL.md         [Response templates]
    ├── legal-risk-assessment/SKILL.md    [Risk frameworks]
    └── meeting-briefing/SKILL.md         [Meeting prep]
```

### 5.2 Contract Review Skill Contents

**Document-by-document analysis without file access** — the skill provides methodology for Claude to apply to any contract text.

**Key Sections:**
1. **Loading the Playbook** — How to find and apply org-specific legal playbook
2. **Review Process** — 4-step methodology (identify type, determine side, read entire contract, analyze clauses)
3. **Common Clause Analysis** — Deep documentation of 8+ clause types
   - Limitation of Liability (cap amount, carveouts, mutual vs. unilateral, consequential damages)
   - Indemnification (scope, mutual, cap, IP, data breach)
   - IP Ownership (pre-existing, developed, work-for-hire, licenses)
   - Data Protection (DPA, processing, sub-processors, breach notification, transfers)
   - Term and Termination (duration, renewal, termination for convenience/cause)
   - Governing Law (jurisdiction, dispute resolution)

4. **Deviation Severity Classification**
   - **GREEN** — Acceptable (note for awareness, no negotiation needed)
   - **YELLOW** — Negotiate (outside standard but within range, generate redlines)
   - **RED** — Escalate (outside acceptable, requires counsel review)

5. **Redline Generation** — Specific format and content requirements
6. **Negotiation Priority Framework** — Tier 1 (must-haves), Tier 2 (should-haves), Tier 3 (nice-to-haves)

### 5.3 Compliance Skill (Privacy/Regulations)

Comprehensive coverage of:
- **GDPR** — Articles, key obligations, in-house legal touchpoints
- **CCPA/CPRA** — Consumer rights, response timelines, non-discrimination
- **LGPD, POPIA, PIPEDA, PDPA, UK GDPR** — International requirements
- **DPA Review Checklist** — 100+ items covering GDPR Article 28 requirements
- **Data Subject Request Handling** — Intake, verification, response processes
- **Regulatory Monitoring** — What to track and escalation criteria

### 5.4 NDA Triage Skill (Example of Classification)

Systematically evaluates NDAs on **10 criteria**, each with sub-checks:

1. **Agreement Structure** — Type, appropriateness, standalone vs. embedded
2. **Definition of Confidential Information** — Scope, marking, exclusions
3. **Obligations of Receiving Party** — Standard of care, use restriction
4. **Standard Carveouts** — Public knowledge, prior possession, independent development, third-party receipt, legal compulsion
5. **Permitted Disclosures** — Employees, contractors, advisors, affiliates, legal/regulatory
6. **Term and Duration** — Agreement term, survival period
7. **Return and Destruction** — Obligations, exceptions, certification
8. **Remedies** — Injunctive relief, pre-determined damages
9. **Problematic Provisions** — Non-solicitation, non-compete, exclusivity, standstill
10. **Governing Law and Jurisdiction** — Jurisdiction reasonableness

**Classification Rules:**
- **GREEN** — All criteria met, standard carveouts present, no problematic provisions
- **YELLOW** — 1+ criteria imperfect but not fundamentally problematic
- **RED** — 1+ critical criteria missing or fundamentally problematic provisions present

---

## 6. SKILL INTEGRATION PATTERNS

### 6.1 Plugin Manifest (plugin.json)

Minimal JSON structure:

```json
{
  "name": "legal",
  "version": "1.0.0",
  "description": "Speed up contract review, NDA triage, and compliance workflows...",
  "author": {
    "name": "Anthropic"
  }
}
```

The manifest is **mainly metadata** — the real integration happens via file organization.

### 6.2 MCP Configuration (.mcp.json)

Tools are connected via MCP (Model Context Protocol) servers:

```json
{
  "mcpServers": {
    "slack": {
      "type": "http",
      "url": "https://mcp.slack.com/mcp"
    },
    "box": {
      "type": "http",
      "url": "https://mcp.box.com"
    },
    "egnyte": {
      "type": "http",
      "url": "https://mcp-server.egnyte.com/mcp"
    },
    "atlassian": {
      "type": "http",
      "url": "https://mcp.atlassian.com/v1/mcp"
    },
    "ms365": {
      "type": "http",
      "url": "https://microsoft365.mcp.claude.com/mcp"
    }
  }
}
```

**Key Points:**
- **Tool-agnostic placeholders** — Skills use `~~chat`, `~~cloud storage`, etc.
- **Category-based** — Any MCP server in that category works (Slack, Teams, etc.)
- **Pre-configured** — Each plugin includes typical servers; users can customize
- **Graceful degradation** — Skills work without connected tools, noting gaps

### 6.3 Commands (Explicit Slash Commands)

Commands are optional explicit entry points that invoke skills.

**File Format:** `commands/command-name.md`

```yaml
---
description: Review a contract against your organization's negotiation playbook...
argument-hint: "<contract file or text>"
---

# /review-contract -- Contract Review Against Playbook

[Detailed workflow]
```

**Command Structure:**
1. **Description** — What the command does, when to use it
2. **Argument hint** — What the user should provide
3. **Workflow** — Step-by-step process
4. **Output Format** — Structured output template

### 6.4 Can Multiple Skills Be Combined?

**Yes, transparently.**

Skills reference each other:
- draft-outreach skill explicitly mentions using research-prospect skill internally
- cowork-plugin-customizer skill orchestrates multiple sub-skills
- Skills can be layered (contract-review + legal-risk-assessment for final assessment)

**There's no explicit composition mechanism** — Claude applies relevant skills based on the task.

### 6.5 Skill Dependencies

Skills are **loosely coupled**:
- Some expect certain tools to be connected (contract-review expects cloud storage)
- Some degrade gracefully (work with or without MCP tools)
- Some require configuration files (legal playbook for contract-review)

**Dependency is documented in skill description**, e.g.:
```
Use when reviewing contracts against your negotiation playbook.
Works best with cloud storage connected.
If no playbook configured, offers to help create one.
```

---

## 7. FILE SEARCH & DOCUMENT ANALYSIS SKILLS

The repository includes several skills for document/file analysis, relevant to your S3 search project:

### 7.1 Knowledge Management Skill (Customer Support)

Document analysis skill for turning support tickets into KB articles:

**Focuses on:**
- Article structure and formatting standards
- Writing for searchability (titles, keywords, customer language)
- Multiple article types (how-to, troubleshooting, FAQ, known issues)
- Content organization and categorization taxonomy
- Linking and cross-referencing strategy

**Useful for:** Structured documentation generation from unstructured content

### 7.2 Data Context Extractor Skill (Data Plugin)

**Meta-skill** for bootstrapping data analysis capabilities:

Two modes:
1. **Bootstrap Mode** — Create company-specific data skill from scratch
   - Database discovery (schemas, tables)
   - Entity disambiguation
   - Metric definition extraction
   - Common gotchas identification

2. **Iteration Mode** — Add domain context to existing skills

**Structure Generated:**
```
company-data-analyst/
├── SKILL.md
└── references/
    ├── entities.md
    ├── metrics.md
    ├── tables/
    │   ├── domain1.md
    │   └── domain2.md
    └── dashboards.json
```

**Relevant** for: Extracting structure from document collections

### 7.3 Search Strategy Skill (Enterprise Search)

Query decomposition and multi-source orchestration:

**Handles:**
- Query type classification (decision, status, document, person, factual, temporal, exploratory)
- Search component extraction (keywords, entities, intent signals, constraints)
- Source-specific query translation (different syntax for Slack, Wiki, Task tracker)
- Result ranking and deduplication
- Ambiguity handling
- Fallback strategies for unavailable sources

**Useful for:** Intelligent search across heterogeneous data sources

---

## 8. DEPLOYMENT & PACKAGING GUIDANCE

### 8.1 Plugin Installation

**Claude Code:**
```bash
# Add the marketplace
claude plugin marketplace add anthropics/knowledge-work-plugins

# Install a specific plugin
claude plugin install sales@knowledge-work-plugins
```

**Cowork (Desktop App):**
- Install directly from [claude.com/plugins](https://claude.com/plugins/)

### 8.2 Plugin Customization Workflow

The `cowork-plugin-management` plugin provides meta-capabilities for customization:

**Process:**
1. **Identify customization points** — Grep for `~~` placeholders
2. **Gather organizational context** — Search Slack, docs, email via knowledge MCPs
3. **Replace placeholders** — Update tool names, process names, config values
4. **Connect MCPs** — Search registry and connect relevant servers
5. **Package as .plugin file** — Zip the customized plugin directory
6. **Distribute** — Share .plugin file for team installation

**Customization Example:**
```
Original:  "Save to ~~cloud storage"
Customized: "Save to Box"

Original:  Use ~~project tracker for task management
Customized: Use Asana for task management
```

### 8.3 .plugin File Format

Customized plugins are packaged as `.plugin` files (ZIP archives):

```bash
cd /path/to/plugin && zip -r plugin-name.plugin . -x "setup/*"
```

Contains:
- All skill files (SKILL.md)
- Customized command files
- Updated .mcp.json with organization's tools
- .claude-plugin/plugin.json manifest
- Any reference files or documentation

### 8.4 Plugin Distribution Patterns

**Three patterns observed:**

1. **Template/Generic** — Distributed via GitHub, customized locally
   - User clones plugin
   - Customizes for their org
   - Installs locally

2. **Marketplace** — Pre-built plugins installable directly
   - Minimal customization needed
   - Reasonable defaults for most teams
   - Optional local customization

3. **Organization-Specific** — Custom plugins for particular tools/workflows
   - Built using cowork-plugin-management plugin
   - Packaged as .plugin file
   - Distributed within organization

---

## 9. CONFIGURATION & EXTENSION

### 9.1 Local Configuration Files

Plugins support local configuration via `.local.md` files:

**Example (Legal Plugin):**
```
.claude/legal.local.md
```

**Contents:**
- Organization's contract negotiation playbook
- Standard legal positions and acceptable ranges
- Escalation triggers
- Response templates
- Risk assessment framework customizations

### 9.2 Reference Files

Skills can include reference materials:

```
skill-name/
├── SKILL.md
└── references/
    ├── entities.md
    ├── metrics.md
    ├── tables/
    │   └── domain1.md
    └── sample-queries.sql
```

**Used by data-context-extractor to bootstrap company-specific analysis skills**

### 9.3 Customization Points (Placeholders)

Generic plugins use `~~` prefix for customization points:

```markdown
Save to ~~cloud storage using ~~e-signature for signing
Post updates to ~~chat channel for team visibility
```

**Customization workflow:**
1. Find all `~~` placeholders
2. Replace with actual tool names from org
3. Update .mcp.json with corresponding servers
4. Package as .plugin file

---

## 10. KEY INSIGHTS & BEST PRACTICES

### 10.1 Skills Are Pure Knowledge, No Code

- **Pure markdown with YAML frontmatter**
- No Python, JavaScript, or any programming language
- No state management or configuration beyond frontmatter
- All logic is expressed as procedural guidance

**Implication:** Skills are easy to audit, modify, and version control. Anyone can understand and customize them.

### 10.2 Skills Encode Organizational Patterns

Skills are most powerful when customized with org-specific:
- Playbooks (legal positions, negotiation strategies)
- Terminology (how the org refers to concepts)
- Processes (step-by-step workflows)
- Standards (quality checks, review requirements)

**Without customization:** Generic but useful
**With customization:** Organization-specific AI agent

### 10.3 Skills Enable Consistency at Scale

By encoding domain expertise once in a skill, every instance of Claude using that plugin applies the same methodology:

- **Legal:** Every contract reviewed using same framework
- **Sales:** Every outreach follows same research-then-draft pattern
- **Finance:** Every reconciliation uses same methodology
- **Data:** Every query uses same SQL generation approach

### 10.4 Multi-Skill Orchestration

Complex workflows aren't monolithic skills — they're compositions:

**Example:** /call-summary command
1. Extract discussion points (core skill)
2. Identify action items (methodology)
3. Draft follow-up email (response drafting skill)
4. Update CRM (tool integration via MCP)

All transparent to the user.

### 10.5 Tool-Agnostic Design

Plugins don't hard-code dependencies on specific tools. Instead:
- Use category placeholders (`~~chat`, `~~cloud storage`)
- Pre-configure typical servers in `.mcp.json`
- Users can swap tools by updating MCP config
- Skills degrade gracefully when tools aren't available

**Example:**
```
Original: "Search ~~chat for recent decisions"
Org 1 uses Slack: MCP server searches Slack
Org 2 uses Teams: MCP server searches Teams
Org 3 has neither: Skill notes the gap, proceeds without
```

---

## 11. PRODUCTION DEPLOYMENT EXAMPLE

**Scenario:** A legal team wants to deploy the legal plugin

### Phase 1: Evaluation
- Review legal plugin README and skills
- Assess applicability to firm's practices

### Phase 2: Customization
- Create `legal.local.md` with firm's playbook:
  - Standard liability cap (e.g., 12 months of fees)
  - IP ownership positions
  - Data protection requirements
  - Escalation triggers
  - Response templates

### Phase 3: Tool Integration
- Update `.mcp.json` to connect firm's tools:
  - Slack for notifications
  - Box or Egnyte for document storage
  - Atlassian for matter tracking
  - Microsoft 365 for email/calendar

### Phase 4: Team Training
- Walk team through /review-contract workflow
- Show how contract-review skill applies playbook
- Demonstrate RED flag escalation process
- Explain how to add new response templates

### Phase 5: Deployment
- Install plugin in Cowork or Claude Code
- Test on sample contracts
- Customize playbook based on feedback
- Roll out to broader team

### Phase 6: Iteration
- Monitor RED flag escalations
- Update playbook as market positions shift
- Add new response templates as needed
- Measure time savings in contract review

---

## 12. COMPARISON TO OTHER APPROACHES

| Aspect | Skills | Traditional Agents | Prompt Engineering | Fine-Tuning |
|--------|--------|------------------|-------------------|-----------|
| **Format** | Markdown files | Code (Python, etc.) | Text prompts | Training data + model weights |
| **Maintenance** | Easy (edit .md) | Requires coding | Fragile (prompt drift) | Expensive, requires retraining |
| **Customization** | Straightforward | Code changes needed | Limited | Very expensive |
| **Version Control** | Excellent (Git) | Standard | Text diffs | Complex |
| **Auditability** | Transparent | Code review needed | Clear but limited | Black box |
| **Scalability** | 100+ skills in one repo | Code complexity grows | Prompt length limits | Training cost |
| **Non-technical adoption** | High (just Markdown) | Low (requires dev) | Medium | Very low |

---

## CONCLUSION

Claude skills represent a **declarative, file-based approach to building specialized AI agents**. By encoding domain expertise as Markdown documentation rather than code, they make it possible for non-technical domain experts to define how Claude should operate in their domain.

The knowledge-work-plugins repository demonstrates mature patterns for:
- Encoding complex domain knowledge (legal, finance, sales, etc.)
- Organizing skills into coherent plugins
- Connecting to external tools via MCP
- Customizing for specific organizations
- Distributing and versioning plugins

**For your S3 search project:** The search-strategy and data-context-extractor skills show how Claude can orchestrate multi-source document retrieval and extract structure from unstructured content.

