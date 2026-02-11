# Claude Skill File Format Reference

## Quick Start

A Claude skill is a Markdown file with YAML frontmatter that encodes domain expertise and methodology.

```markdown
---
name: skill-id
description: Brief description of when to use this skill
---

# Skill Title

Introduction and overview of what this skill covers.

## Section 1: Core Concept
Content explaining the methodology...

## Section 2: Process Steps
Step-by-step instructions...

## Section 3: Best Practices
Guidelines and recommendations...
```

---

## File Structure

**Location:** `plugin-name/skills/skill-name/SKILL.md`

**Naming conventions:**
- Directory name: kebab-case (e.g., `contract-review`)
- File name: `SKILL.md` (always)
- `name` field in frontmatter: kebab-case (e.g., `contract-review`)

---

## Frontmatter Schema

### Required Fields

```yaml
---
name: skill-identifier
description: One-sentence description of when Claude should use this skill
---
```

- **`name`**: Unique identifier (kebab-case). Used internally for skill identification.
- **`description`**: Trigger description explaining when the skill applies. Should be concise and actionable.

### Optional Fields

```yaml
---
name: skill-id
description: Description
compatibility: Optional compatibility notes (e.g., "Requires Cowork desktop app")
---
```

---

## Content Structure (Best Practices)

Skills typically include these sections:

### 1. Introduction / Context
```markdown
# Skill Title

[1-2 sentence overview of what this skill covers]

This skill helps with [X] by [methodology/approach].
```

### 2. Domain Knowledge Sections
```markdown
## [Concept 1]

[Explanation of how to think about this concept]

### Sub-concept 1a
[Details]

### Sub-concept 1b
[Details]
```

### 3. Methodology / Process
```markdown
## [Process Name] Methodology

### Step 1: [Phase]
[What to do, how to think about it, what to look for]

### Step 2: [Phase]
[Next phase...]
```

### 4. Classification Frameworks
```markdown
## Classification Rules

### GREEN -- [Category A]
[Description of when something is in this category]
- [Characteristics]
- [Actions to take]

### YELLOW -- [Category B]
[Description of when something is in this category]

### RED -- [Category C]
[Description of when something is in this category]
```

### 5. Checklists / Evaluation Criteria
```markdown
## Evaluation Checklist

When assessing X, verify:
- [ ] **Criterion 1** — [What to check]
- [ ] **Criterion 2** — [What to check]
- [ ] **Criterion 3** — [What to check]
```

### 6. Best Practices / Guidelines
```markdown
## Best Practices

When doing X:
1. **Practice 1** — [When and how to apply it]
2. **Practice 2** — [When and how to apply it]
```

### 7. Templates / Output Formats
```markdown
## Output Format

Provide responses in this structure:
```
[Template example]
```
```

### 8. Examples
```markdown
## Example

**Scenario:** [Context]
**Input:** [What the user provides]
**Output:** [What the skill generates]

[Full worked example]
```

### 9. Edge Cases / Escalation Triggers
```markdown
## Escalation Triggers

When you encounter these situations, escalate rather than proceeding:
- [Trigger 1 and why]
- [Trigger 2 and why]
```

---

## Key Principles

1. **No Code** — Skills are pure Markdown. No Python, JavaScript, or other languages.

2. **Behavioral Instruction** — Focus on teaching how Claude should think and approach problems, not just what to output.

3. **Procedural Guidance** — Use step-by-step processes, checklists, and frameworks rather than abstract concepts.

4. **Actionability** — Every section should guide Claude toward a concrete action or decision.

5. **Transparency** — Explain the reasoning behind each approach, not just the rules.

6. **Customization Points** — Identify where org-specific information should be inserted or loaded.

7. **Graceful Degradation** — Design skills to work with or without external tools/data.

---

## Real-World Skill Structure: Contract Review

```markdown
---
name: contract-review
description: Review contracts against your organization's negotiation playbook, 
  flagging deviations and generating redline suggestions.
---

# Contract Review Skill

You are a contract review assistant for an in-house legal team...

## Playbook-Based Review Methodology

### Loading the Playbook
Before reviewing any contract, check for a configured playbook...

### Review Process
1. **Identify contract type**: SaaS, professional services, license, partnership...
2. **Determine user's side**: Vendor, customer, licensor...
3. **Read the entire contract** before flagging issues...
4. **Analyze each material clause** against the playbook...

### Common Clause Analysis

#### Limitation of Liability
**Key elements to review:**
- Cap amount (fixed dollar amount, multiple of fees, uncapped)
- Whether the cap is mutual...

## Deviation Severity Classification

### GREEN -- Acceptable
The clause aligns with or is better than the organization's standard position.
- Examples: [specific examples]
- Action: Note for awareness. No negotiation needed.

### YELLOW -- Negotiate
The clause falls outside the standard position but within negotiable range.
- Examples: [specific examples]
- Action: Generate specific redline language...

### RED -- Escalate
The clause falls outside acceptable range or triggers escalation criterion.
- Examples: [specific examples]
- Action: Explain the specific risk...

## Redline Generation Best Practices

When generating redline suggestions:
1. **Be specific**: Provide exact language...
2. **Be balanced**: Propose firm but commercially reasonable language...

### Redline Format

For each redline:
```
**Clause**: [Section reference]
**Current language**: "[exact quote]"
**Proposed redline**: "[alternative language]"
**Rationale**: [1-2 sentences explaining why]
**Priority**: [Must-have / Should-have / Nice-to-have]
**Fallback**: [Alternative if primary rejected]
```
```

---

## Integration with Plugins

Skills sit within plugins:

```
plugin-name/
├── .claude-plugin/plugin.json
├── .mcp.json                      # Tool/connector configuration
├── README.md                       # Plugin overview
├── CONNECTORS.md                   # Tool reference info
├── commands/                       # Explicit slash commands
│   ├── command1.md
│   └── command2.md
└── skills/                         # Domain expertise
    ├── skill-name-1/
    │   └── SKILL.md
    ├── skill-name-2/
    │   ├── SKILL.md
    │   └── references/
    │       ├── guide1.md
    │       └── guide2.md
```

---

## Tips for Creating Skills

1. **Start with a real workflow** — Base the skill on actual processes your team uses.

2. **Encode decisions** — Include decision frameworks (checklists, classification rules) that would normally require expert judgment.

3. **Surface gotchas** — Document edge cases and common mistakes.

4. **Make it scannable** — Use headers, bullet points, and tables for easy reference.

5. **Include examples** — Real or realistic examples help Claude understand intent.

6. **Handle uncertainty** — Explain when to escalate or ask for clarification.

7. **Support customization** — Design skills to work with local configuration files or allow org-specific values to be injected.

8. **Test the methodology** — Have non-experts follow your skill's guidance and see if they get the right results.

---

## Example: Minimal Skill

```markdown
---
name: example-skill
description: Use when you need to do X. Triggers: "help me X", "I need to X"
---

# Example Skill

This skill helps Claude approach X by using methodology Y.

## Core Approach

The key insight: [explain the mental model]

## Process

When the user asks you to do X:

1. **Understand context** — Ask: [clarifying questions]
2. **Gather information** — Look for: [what matters]
3. **Apply methodology** — Use [the framework]
4. **Output result** — Format as: [structure]

## Framework

Use this decision tree:
- If [condition A], then [approach 1]
- If [condition B], then [approach 2]
- Otherwise, [approach 3]

## Examples

**Scenario 1:** [User describes situation]
- Follow step 1: [output]
- Follow step 2: [output]
- Result: [final output]

## When to Escalate

Escalate if:
- [Trigger 1]
- [Trigger 2]
```

---

## Distribution & Usage

Skills become available to Claude when a plugin is installed:

```bash
# Installation
claude plugin install plugin-name

# Automatic activation
# Claude detects when skill knowledge is relevant and applies it
# No explicit invocation needed
```

Commands provide explicit entry points:

```bash
# Usage
/command-name [arguments]
```

---

See `/tmp/knowledge-work-plugins/legal/skills/contract-review/SKILL.md` for a comprehensive real-world example.

