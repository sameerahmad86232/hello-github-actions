# Swarm Studio Codex rules
When the user requests Swarm Studio, read `.agents/skills/swarm-studio/SKILL.md` and `config/roles.json`.
Treat all 20 roles as named professions, not guaranteed simultaneous processes. Use Codex's supported native subagents for independent jobs only; otherwise execute them sequentially and report actual concurrency.
Do not replace original repository files outside this `swarm-studio/` folder. Never claim simulated events represent live subagent activity.
Generated website projects are created inside `workspace/`, which is gitignored.
