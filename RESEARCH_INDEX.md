# Claude Skills Research - Complete Index

**Research Date:** February 10, 2026
**Repository:** https://github.com/anthropics/knowledge-work-plugins
**Status:** Comprehensive research completed
**Total Plugins Analyzed:** 11
**Total Skills Documented:** 53+
**Files Created:** 3 detailed research documents

---

## Files in This Research

### 1. CLAUDE_SKILLS_RESEARCH.md (771 lines)
**Comprehensive 12-section research document**

Complete deep-dive into Claude skills architecture, format, and implementation patterns.

**Contents:**
1. Skill Format & Structure — YAML/Markdown file format, schema, components
2. Skill Categories & Available Skills — Complete inventory of 11 plugins and 53+ skills
3. How Skills Work — Invocation mechanism, triggering, composition
4. Skill Components in Detail — Instruction vs. tools, domain expertise encoding
5. Legal Skill Deep-Dive — Detailed example of contract-review, NDA triage, compliance skills
6. Skill Integration Patterns — Plugin manifest, MCP configuration, commands, composition
7. File Search & Document Analysis Skills — Knowledge-management, data-context-extractor, search-strategy
8. Deployment & Packaging Guidance — Installation, customization workflow, .plugin format, distribution
9. Configuration & Extension — Local config files, reference files, customization points
10. Key Insights & Best Practices — Core principles, consistency, tool-agnostic design
11. Production Deployment Example — Real-world legal team deployment scenario
12. Comparison to Other Approaches — Skills vs. traditional agents, prompt engineering, fine-tuning

**Audience:** Architects, decision-makers, anyone needing comprehensive understanding

**Key Takeaway:** Skills are Markdown-based behavioral instructions that encode domain expertise without code.

---

### 2. SKILL_FORMAT_REFERENCE.md (373 lines)
**Quick reference guide for skill file format**

Practical guide for understanding and creating skills.

**Contents:**
- Quick start example
- File structure and naming conventions
- Frontmatter schema (required and optional fields)
- Content structure best practices
- Key principles (no code, behavioral instruction, procedural guidance)
- Real-world example structure (contract-review skill)
- Plugin integration diagram
- Tips for creating skills
- Minimal skill example
- Distribution and usage patterns

**Audience:** Developers, skill creators, anyone implementing skills

**Key Takeaway:** Skills follow a consistent Markdown format with YAML frontmatter. Pure instruction, no code.

---

### 3. SKILL_TYPES_AND_EXAMPLES.md (515 lines)
**Catalog of all skill types with detailed examples**

Complete inventory of available skills organized by domain and use case.

**Covers:**
1. Legal & Compliance (contract-review, nda-triage, compliance, canned-responses)
2. Sales & Outreach (draft-outreach, account-research, call-prep, competitive-intelligence)
3. Finance & Accounting (journal-entry, reconciliation, financial-statements, variance-analysis)
4. Data & Analytics (sql-queries, statistical-analysis, data-validation, data-context-extractor)
5. Customer Support (ticket-triage, response-drafting, knowledge-management)
6. Marketing & Brand (brand-voice, content-creation, campaign-planning)
7. Product Management (feature-spec, roadmap-management, user-research, metrics)
8. Enterprise Search (search-strategy, knowledge-synthesis)
9. Productivity (task-management, meeting-briefing)
10. Scientific Research (literature-search, target-prioritization)
11. Plugin Management (plugin-customizer, plugin-creator)

**Each skill includes:**
- Use case description
- How it works
- Key components
- Example output

**Plus:**
- Skill composition patterns
- How to find the right skill
- Summary of capabilities

**Audience:** Business users, team leads, anyone evaluating skills for their team

**Key Takeaway:** 53+ documented skills across 11 business functions, from legal to science research.

---

## Quick Navigation

### If you want to understand...

**Skill file format and structure:**
→ Read SKILL_FORMAT_REFERENCE.md sections 1-2

**How skills are triggered and composed:**
→ Read CLAUDE_SKILLS_RESEARCH.md section 3

**The legal skill example in detail:**
→ Read CLAUDE_SKILLS_RESEARCH.md section 5

**All available skills by type:**
→ Read SKILL_TYPES_AND_EXAMPLES.md sections 1-11

**How to deploy skills in production:**
→ Read CLAUDE_SKILLS_RESEARCH.md sections 8-9, and section 11

**How skills differ from other approaches:**
→ Read CLAUDE_SKILLS_RESEARCH.md section 12

**Key principles and best practices:**
→ Read CLAUDE_SKILLS_RESEARCH.md section 10

---

## Research Highlights

### Format & Structure
- **File Format:** Markdown (.md) with YAML frontmatter
- **File Location:** `plugin-name/skills/skill-name/SKILL.md`
- **Frontmatter:** `name`, `description`, optional `compatibility`
- **No Code:** Pure instruction and knowledge documentation

### Key Findings on How Skills Work
- **Not Tools:** Skills are behavioral instructions, not tool definitions
- **System Prompt Integration:** Skills are embedded in Claude's system prompt
- **Automatic Triggering:** Skills activate based on relevance detection
- **Multi-Skill Composition:** Skills transparently reference and compose with each other
- **Tool-Agnostic:** Skills use category placeholders (`~~chat`, `~~cloud storage`); tools are configured separately

### Legal Plugin Example (Most Comprehensive)
The legal plugin demonstrates sophisticated document analysis patterns:

**6 Skills:**
1. contract-review — Playbook-based contract analysis with clause-by-clause review
2. nda-triage — 10-point NDA evaluation with GREEN/YELLOW/RED classification
3. compliance — Privacy regulations (GDPR, CCPA, LGPD, etc.) and DPA review
4. canned-responses — Template management with smart escalation detection
5. legal-risk-assessment — Risk classification frameworks
6. meeting-briefing — Meeting prep methodology

**Key Pattern:** Each skill encodes what would normally require hiring a specialist, making that expertise reusable across the team.

### Skill Deployment Patterns
Three patterns for distributing skills:
1. **Template/Generic** — Clone and customize for your org
2. **Marketplace** — Pre-built, installable with minimal customization
3. **Organization-Specific** — Customized `.plugin` file for team distribution

---

## Document Inventory by Use Case

### For Architects / Product Decisions
Start with: CLAUDE_SKILLS_RESEARCH.md
- Understand the complete architecture
- See how it compares to alternatives
- Understand customization and distribution patterns

### For Implementation / Skill Creation
Start with: SKILL_FORMAT_REFERENCE.md
- Understand the Markdown format
- See examples of skill structure
- Follow tips for creating new skills

### For Evaluating Skills for Your Team
Start with: SKILL_TYPES_AND_EXAMPLES.md
- See what skills exist
- Understand what each skill does
- Find skills relevant to your domain

### For Deep Understanding of Specific Domains
Go to: CLAUDE_SKILLS_RESEARCH.md, Section 5
- Legal skill example is most detailed
- Shows sophisticated document analysis patterns
- Demonstrates how to encode domain expertise

---

## Key Statistics

| Metric | Count |
|--------|-------|
| Total plugins | 11 |
| Total skills | 53+ |
| Total lines of research | 1,659 |
| Plugins analyzed in detail | 5 (legal, sales, finance, data, support) |
| Legal skill sections | 6 major skills with 100+ pages of methodology |
| Skill file components examined | 50+ individual skill files |
| Real-world examples provided | 30+ |

---

## Source Materials

All analysis based on direct examination of:
- `/tmp/knowledge-work-plugins/` — GitHub repository clone
- 50+ individual `SKILL.md` files
- 11 plugin manifests and configurations
- Complete plugin documentation and READMEs
- Real command files and MCP configurations

---

## Summary

This research package provides:

1. **Complete understanding** of how Claude skills work (format, integration, triggering)
2. **Practical guidance** for creating and customizing skills
3. **Comprehensive catalog** of 53+ available skills organized by domain
4. **Real-world examples** showing skills in production deployment
5. **Strategic insights** on skill architecture and best practices

The three documents work together:
- CLAUDE_SKILLS_RESEARCH.md provides depth and architecture
- SKILL_FORMAT_REFERENCE.md provides practical implementation guidance
- SKILL_TYPES_AND_EXAMPLES.md provides a searchable catalog and quick reference

---

## Next Steps

To use this research:

1. **Understand the format** — Read SKILL_FORMAT_REFERENCE.md
2. **Evaluate for your use case** — Check SKILL_TYPES_AND_EXAMPLES.md for relevant skills
3. **Understand architecture** — Review CLAUDE_SKILLS_RESEARCH.md as needed for depth
4. **Create or customize** — Use the format reference and examples to build skills
5. **Deploy** — Follow deployment patterns from the comprehensive research document

---

**Created:** February 10, 2026
**Repository Analyzed:** https://github.com/anthropics/knowledge-work-plugins
**Status:** Research complete and documented

