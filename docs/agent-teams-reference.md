# Agent Teams — Master Reference Guide

Source: https://code.claude.com/docs/en/agent-teams  
Requires: Claude Code v2.1.32+, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

---

## What Are Agent Teams?

Agent teams coordinate multiple Claude Code instances working together. One session acts as **team lead** — it creates the team, spawns teammates, manages the task list, and synthesizes results. Each **teammate** is a fully independent Claude Code session with its own context window.

Unlike subagents (which only report back to the caller), teammates can message each other directly and self-coordinate via a shared task list.

---

## Enable Agent Teams

Set in `.claude/settings.local.json` (project-local) or `~/.claude/settings.json` (global):

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Or export in your shell: `export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

---

## Agent Teams vs. Subagents

| Dimension | Subagents | Agent Teams |
|---|---|---|
| Context | Own context; results return to caller | Own context; fully independent |
| Communication | Report to main agent only | Teammates message each other directly |
| Coordination | Main agent manages all work | Shared task list + self-coordination |
| Best for | Focused tasks where only the result matters | Complex work needing discussion and collaboration |
| Token cost | Lower (results summarized back) | Higher (each teammate is a separate Claude instance) |

**Rule of thumb:** Use subagents when you need quick, focused workers that report back. Use agent teams when teammates need to share findings, challenge each other, and coordinate on their own.

---

## Architecture

| Component | Role |
|---|---|
| Team lead | Main session — creates team, spawns teammates, manages task list |
| Teammates | Independent Claude Code instances working assigned tasks |
| Task list | Shared work items with pending / in-progress / completed states + dependency tracking |
| Mailbox | Messaging system for direct agent-to-agent communication |

**Storage locations (auto-managed, do not edit by hand):**
- Team config: `~/.claude/teams/{team-name}/config.json`
- Task list: `~/.claude/tasks/{team-name}/`

The `config.json` holds runtime state (session IDs, tmux pane IDs) and is overwritten on every state change. To define reusable teammate roles, use subagent definitions — not the team config.

---

## Starting a Team

Just describe the task and team structure in natural language. Claude creates the team, spawns teammates, and coordinates work.

**Example prompt:**
```
I'm designing a CLI tool that helps developers track TODO comments across
their codebase. Create an agent team to explore this from different angles:
one teammate on UX, one on technical architecture, one playing devil's advocate.
```

Claude will:
1. Create a team with a shared task list
2. Spawn a teammate per role
3. Have them explore the problem
4. Synthesize findings
5. Clean up the team when finished

Teams are also proposed by Claude autonomously if it determines a task benefits from parallel work — but it always asks for confirmation first.

---

## Display Modes

| Mode | How it works | Requirement |
|---|---|---|
| `in-process` (default) | All teammates run inside your main terminal. `Shift+Down` cycles through them. | Any terminal |
| `tmux` | Each teammate gets its own pane; see all output at once | tmux or iTerm2 + `it2` CLI |
| `auto` | Uses split panes if already inside tmux, otherwise in-process | — |

Set in `~/.claude/settings.json`:
```json
{ "teammateMode": "in-process" }
```

Or force for one session: `claude --teammate-mode in-process`

**iTerm2 setup:** Install `it2` CLI, then enable Python API in iTerm2 → Settings → General → Magic → Enable Python API.

**Navigation in in-process mode:**
- `Shift+Down` — cycle through teammates
- `Enter` — view a teammate's session
- `Escape` — interrupt their current turn
- `Ctrl+T` — toggle the task list

---

## Controlling the Team

All control goes through natural language to the lead. Key patterns:

### Specify teammates and models
```
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

### Require plan approval before implementation
```
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```
The lead autonomously approves/rejects plans. Influence its judgment with criteria in your prompt: "only approve plans that include test coverage."

### Talk to a teammate directly
In in-process mode: `Shift+Down` to the teammate, then type.  
In split-pane mode: click into the pane.

### Assign tasks explicitly vs. self-claim
- **Lead assigns**: tell the lead which task goes to which teammate
- **Self-claim**: after finishing a task, a teammate picks up the next unassigned, unblocked task on its own
- File locking prevents race conditions when multiple teammates try to claim the same task

### Shut down a teammate
```
Ask the researcher teammate to shut down
```
The teammate can accept (exits gracefully) or reject with an explanation.

### Clean up the team
```
Clean up the team
```
Always run cleanup from the **lead**, not a teammate. Cleanup fails if any teammates are still running — shut them down first.

---

## Task Management

Tasks have three states: **pending → in progress → completed**  
Tasks can have dependencies; a task with unresolved dependencies cannot be claimed until those are completed. Dependency resolution is automatic.

**If the lead starts doing work instead of delegating:**
```
Wait for your teammates to complete their tasks before proceeding
```

**If a task appears stuck (status lag is a known limitation):**
Check if the work is actually done, then tell the lead to update the task status or nudge the teammate.

---

## Context and Communication

- Teammates load the same project context as a regular session: CLAUDE.md, MCP servers, skills
- The lead's conversation history does **not** carry over to teammates
- Task-specific details must be included in the spawn prompt
- Messages between agents are delivered automatically (no polling)
- Teammates notify the lead automatically when they go idle
- Teammates are addressed by name; the lead assigns names at spawn time

**To get predictable names:** tell the lead what to call each teammate in the spawn instruction.

**To reach all teammates:** send one message per recipient (no broadcast).

---

## Subagent Definitions as Teammate Roles

Reference any subagent type (project, user, plugin, or CLI-defined) when spawning:

```
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```

- The definition's `tools` allowlist and `model` are honored
- The definition's body appends to the teammate's system prompt (doesn't replace it)
- Team coordination tools (`SendMessage`, task tools) are always available regardless of `tools` restriction
- `skills` and `mcpServers` frontmatter fields are **not** applied when running as a teammate — those come from project/user settings

---

## Permissions

- Teammates start with the lead's permission settings
- If the lead runs with `--dangerously-skip-permissions`, all teammates do too
- Per-teammate modes can be changed after spawning, but not at spawn time
- To reduce permission prompt interruptions: pre-approve common operations in permission settings before spawning

---

## Quality Gates with Hooks

| Hook | Trigger | Use case |
|---|---|---|
| `TeammateIdle` | Teammate is about to go idle | Exit code 2 → send feedback, keep teammate working |
| `TaskCreated` | A task is being created | Exit code 2 → prevent creation, send feedback |
| `TaskCompleted` | A task is being marked complete | Exit code 2 → prevent completion, send feedback |

---

## Token Costs

Token usage scales linearly with the number of active teammates — each has its own context window. Agent teams cost significantly more than a single session or subagents. Best ROI is on research, review, and new feature work where parallel exploration produces substantially better results.

---

## Best Practices

### Team size
- Start with **3–5 teammates** for most workflows
- Aim for **5–6 tasks per teammate** — keeps everyone productive without excessive context switching
- Scale up only when work genuinely benefits from simultaneous independent exploration
- Three focused teammates often outperform five scattered ones

### Task sizing
- **Too small:** coordination overhead exceeds the benefit
- **Too large:** teammates work too long without check-ins, increasing wasted effort risk
- **Just right:** self-contained units with a clear deliverable (a function, a test file, a review)

### Context quality
Always include task-specific details in spawn prompts — teammates don't inherit conversation history:
```
Spawn a security reviewer with the prompt: "Review src/auth/ for vulnerabilities.
Focus on token handling, session management, and input validation. The app uses
JWT tokens in httpOnly cookies. Report issues with severity ratings."
```

### Avoid file conflicts
Two teammates editing the same file leads to overwrites. Assign each teammate a distinct set of files.

### Monitor and steer
Check in on progress, redirect approaches that aren't working, and synthesize findings as they come in. Don't let teams run unattended too long.

### Start simple
If new to agent teams, begin with read-only tasks (PR review, library research, bug investigation) before tackling parallel implementation.

### Use CLAUDE.md
Teammates read CLAUDE.md from their working directory — use it to give project-specific guidance to all teammates automatically.

---

## Strong Use Cases

| Use case | Why teams work |
|---|---|
| Parallel code review | Each reviewer applies a different lens (security / performance / test coverage) simultaneously without overlap |
| Competing hypotheses debugging | Teammates actively try to disprove each other's theories — the surviving theory is more likely the real root cause |
| New modules / features | Each teammate owns a separate piece with no shared files |
| Cross-layer coordination | Frontend, backend, and tests each owned by a different teammate |
| Research and synthesis | Multiple teammates investigate different aspects, share, and challenge findings |

### When NOT to use agent teams
- Sequential tasks (each step depends on the previous)
- Same-file edits (file conflict risk)
- Work with many cross-cutting dependencies
- Routine, low-complexity tasks (a single session is more cost-effective)

---

## Proven Prompt Patterns

### Parallel code review
```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

### Adversarial debugging
```
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific debate.
Update the findings doc with whatever consensus emerges.
```

### Parallel feature implementation
```
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

### Guarded implementation with plan approval
```
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
Only approve plans that include test coverage.
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Teammates not appearing (in-process) | Press `Shift+Down` — they may already be running but not visible |
| Teammates not appearing (split panes) | Check `which tmux`; verify iTerm2 Python API is enabled |
| Too many permission prompts | Pre-approve common operations in permission settings before spawning |
| Teammate stops on error | `Shift+Down` to check output; give direct instructions or spawn a replacement |
| Lead shuts down before work is done | Tell the lead to keep going; ask it to wait for teammates before proceeding |
| Orphaned tmux sessions | `tmux ls` → `tmux kill-session -t <session-name>` |
| Task status lag / stuck task | Check if work is actually done; tell lead to update status or nudge teammate |

---

## Known Limitations

- **No session resumption with in-process teammates** — `/resume` and `/rewind` do not restore in-process teammates; spawn new ones after resuming
- **Task status lag** — teammates sometimes fail to mark tasks complete, blocking dependent tasks
- **Slow shutdown** — teammates finish their current request before shutting down
- **One team at a time** — clean up the current team before creating a new one
- **No nested teams** — only the lead can spawn/manage teammates
- **Lead is fixed** — the session that creates the team is the lead for its lifetime; no leadership transfer
- **Permissions set at spawn** — per-teammate modes can be changed after spawning but not before
- **Split panes not supported in** VS Code integrated terminal, Windows Terminal, or Ghostty

---

## Quick Reference Card

```
Enable:        CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
Min version:   claude --version  (need v2.1.32+)
Display mode:  teammateMode: "in-process" | "tmux" | "auto"
Navigate:      Shift+Down (cycle), Enter (view), Escape (interrupt), Ctrl+T (task list)
Assign:        Tell the lead in natural language
Shut down:     "Ask the [name] teammate to shut down"
Clean up:      "Clean up the team"  (always via lead, after all teammates shut down)
Team size:     3–5 teammates, 5–6 tasks per teammate
Storage:       ~/.claude/teams/{team}/config.json  |  ~/.claude/tasks/{team}/
```
