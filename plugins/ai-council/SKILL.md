---
name: consult
description: |
  Multi-AI consultation system that orchestrates discussions between Claude, Gemini CLI, Codex CLI, and Perplexity CLI.
  Use when the user says "/consult", "consult", "ask the council", "get AI opinions", "multi-AI discussion",
  "what do the AIs think", or wants to gather perspectives from multiple AI systems on a problem.
  Supports round-robin discussions with iterative feedback between AI agents.
---

# AI Council - Multi-AI Consultation

Orchestrate collaborative discussions between AI CLI tools: Claude, Gemini, Codex, and Perplexity.

## Available AI Agents

| Agent | CLI Command | Non-interactive Flag | Special Capability |
|-------|-------------|---------------------|-------------------|
| Claude | `claude` | `-p "prompt"` | Reasoning, code |
| Gemini | `gemini` | `-p "prompt"` | Multimodal, search |
| Codex | `codex exec` | `"prompt"` | Code generation |
| Perplexity | `pplx` or API | `"prompt"` | Real-time web search |

### Perplexity Setup

Use the Perplexity Sonar API directly:
```bash
curl -s "https://api.perplexity.ai/v1/responses" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"preset":"pro-search","input":"PROMPT"}' | jq -r '.output'
```

Presets: `pro-search` (deep search), `sonar` (fast), `sonar-pro` (balanced)

## Consultation Workflow

### 1. Gather the Question

Ask the user what question or problem they want the council to discuss.

### 2. Select Participants

Default: all three AIs. User may exclude specific agents or include only certain ones.

### 3. Run Round-Robin Discussion

Execute consultation rounds where each AI:
1. Receives the original question plus prior responses
2. Provides its perspective
3. Can agree, disagree, or build upon previous answers

#### Round 1: Initial Responses

Query each AI independently with the original question:

```bash
# Claude
claude -p "Question: {question}" 2>&1

# Gemini
gemini -p "Question: {question}" 2>&1

# Codex
codex exec "Question: {question}" 2>&1
```

#### Round 2+: Iterative Feedback

Include previous responses in the prompt for each subsequent round:

```bash
claude -p "Question: {question}

Previous responses from other AIs:
{formatted_previous_responses}

Consider the above perspectives. Do you agree, disagree, or want to add anything? Be concise." 2>&1
```

### 4. Synthesize Results

After 2-3 rounds (or when consensus emerges), summarize:
- Points of agreement
- Points of disagreement
- Key insights from each AI
- Recommended action or conclusion

## Prompt Templates

### Initial Question Template
```
You are participating in a multi-AI consultation. Answer the following question thoughtfully and concisely.

Question: {question}

Provide your perspective in 2-3 paragraphs.
```

### Follow-up Round Template
```
You are participating in a multi-AI consultation. Here is the question and responses so far:

Question: {question}

Previous responses:
---
{agent_name}: {response}
---

Consider these perspectives. Do you:
1. Agree with any points? Which ones?
2. Disagree with any points? Why?
3. Have additional insights to add?

Be concise (2-3 paragraphs max).
```

### Self-Consultation Template (Claude consulting Claude)
```
You previously responded to this question. Now reconsider your answer given more time to think.

Question: {question}

Your previous response:
{previous_response}

On reflection, would you change or add anything?
```

## Error Handling

- If a CLI is not installed, skip that agent and note it in the output
- If a CLI times out (>60s), capture partial output and continue
- If a CLI returns an error, include the error in the synthesis

## Example Session

User: "consult the council about whether to use TypeScript or JavaScript for a new project"

1. Query Claude, Gemini, and Codex with the question
2. Collect initial responses
3. Share responses with each AI for round 2
4. If significant disagreement, run round 3
5. Synthesize findings and present to user

## Tips

- Keep prompts concise to avoid token limits
- Use `2>&1` to capture both stdout and stderr
- Set reasonable timeouts (60s default)
- For coding questions, the AIs may provide code examples - present these clearly
