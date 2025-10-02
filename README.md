# August - AI Product Manager Telegram Bot

August is an AI-powered Product Manager bot for Telegram that helps you manage development workflows, coordinate specialized agents, and have deep technical discussions about your codebase.

## Overview

August acts as your PM, coordinating a team of 7 specialized AI agents, managing tasks through their lifecycle, and providing project oversight.

## Features

### 🎯 Product Management
- **Task Management**: Create, assign, track, and transition tasks through their lifecycle
- **Team Coordination**: Manages 7 specialized AI agents (Architect, Engineer, Designer, QA, Analyst, Docs)
- **State Machine**: 7 task states with color-coded emojis (Backlog, Planned, In Progress, Review, Done, Blocked, Cancelled)
- **Priority System**: P0-P3 priority levels for effective task prioritization

### 🤖 Intelligent Conversations
- **Deep Technical Discussions**: Ask about code architecture, implementation details, and design decisions
- **Human-like Communication**: Conversational, concise responses - not documentation dumps
- **Smart Routing**: Automatically detects if you want to create tasks, discuss code, or check status
- **GPT-5 Powered**: Uses OpenAI's latest GPT-5 model for deep technical analysis

### 🔄 Vibe Kanban Integration
- **Bidirectional Sync**: Import/export tasks from your local Vibe Kanban board
- **Agent Mapping**: Automatically maps Vibe agents to August agents
- **State Synchronization**: Keeps task states in sync between systems

### 🔔 Proactive Notifications
- **State Change Alerts**: Get notified when tasks change state
- **Daily Summaries**: Morning standup at 9 AM
- **Blocked Task Detection**: Alerts for tasks stuck in blocked state
- **P0 Stale Task Warnings**: Catches critical tasks that aren't moving

### 📱 Telegram-Native UX
- **Interactive Buttons**: Inline keyboard for easy navigation
- **Commands**: `/start`, `/tasks`, `/agents`, `/workload`, `/standup`, `/sync_vibe`
- **Mobile-Friendly**: Optimized for Telegram mobile app

### 👥 Team Agents
- **🎯 August** - Product Manager (master coordinator)
- **🏗️ Architect** - System design and architecture
- **💻 Engineer** - Code implementation and bug fixes
- **🎨 Designer** - UI/UX design
- **🧪 QA** - Testing and quality assurance
- **📊 Analyst** - Data analysis and metrics
- **📝 Docs** - Documentation and technical writing

## Task States

Tasks flow through color-coded states:

- 🆕 **BACKLOG** (Gray) - New, not started
- 📋 **PLANNED** (Blue) - Scheduled for work
- 🏃 **IN_PROGRESS** (Yellow) - Actively being worked
- 👀 **REVIEW** (Orange) - Awaiting review/approval
- ✅ **DONE** (Green) - Completed
- ❌ **BLOCKED** (Red) - Blocked by dependencies
- 🗑️ **CANCELLED** (Dark Gray) - Won't do

## Usage

### Basic Commands

- `/start` - Welcome message with interactive buttons
- `/tasks` - View all tasks with filtering options
- `/agents` - View the development team
- `/workload` - Check agent workload distribution
- `/standup` - Get daily standup summary
- `/sync_vibe` - Sync with Vibe Kanban board

### Creating Tasks

Just ask August naturally:

```
"Create a task to fix the email sync bug"
"We need to implement dark mode"
"Add a task for improving performance"
```

August will:
1. Decide on the right agent (Architect, Engineer, Designer, etc.)
2. Set appropriate priority (P0-P3)
3. Create the task immediately
4. Explain the reasoning

### Technical Discussions

Ask questions about your codebase:

```
"What is the edge function doing?"
"How does the email sync work?"
"Can you explain the authentication flow?"
"Why do we need the cache layer?"
```

August will:
- Use GPT-5 for deep technical analysis
- Respond conversationally (not like documentation)
- Share 2-3 key insights
- Skip obvious details

### Task Status

Check on progress naturally:

```
"What's in progress?"
"Show me blocked tasks"
"What is the team working on?"
```

### Vibe Kanban Integration

If you're using [Vibe Kanban](https://vibekanban.com) locally:

1. Make sure Vibe is running on `http://127.0.0.1:52822`
2. Update `vibe_sync.py` with your project ID
3. Use `/sync_vibe` command
4. Click "⬇️ Import from Vibe" or "⬆️ Export to Vibe"

## Examples

### Creating a Task
```
User: "We need to fix the email sync bug affecting all users"

August: Got it - email sync bug. A few quick questions:
- What's the specific symptom?
- Do we have Sentry errors to reference?

Based on this, I'm thinking:
- Agent: 💻 Engineer (with 🧪 QA for verification)
- Priority: 🔴 P0 (user-facing bug)

Creating task now...
```

### Status Check
```
User: /standup

August: Morning standup:

🏃 In Progress (2)
• Vertex AI migration (engineer)
• Paywall UI design (designer)

👀 In Review (1)
• Cache optimization (architect)

❌ Blocked (1)
• Analytics export (waiting on access)
```

### Sprint Planning
```
User: "What should we focus on next sprint?"

August: Here's what I'm thinking for Sprint 12...
[detailed breakdown with capacity analysis]
```

## Architecture

### Files
- `bot.py` - Main bot application and handlers
- `agents.py` - Agent definitions and expertise
- `task_manager.py` - Task persistence and state machine
- `august_prompt.py` - August's comprehensive system prompt (2000+ tokens)
- `tasks.db` - SQLite database for task storage

### Technology
- **Bot Framework**: python-telegram-bot 20.7
- **AI**: OpenAI GPT-5 (with GPT-4o fallback for non-technical tasks)
- **Database**: SQLite3
- **Language**: Python 3.12+

### Model Selection

August intelligently selects models based on conversation type:

- **Deep Technical** → GPT-5 (4000 tokens) - for architecture discussions
- **Task Status** → GPT-4o-mini (1500 tokens) - fast for status updates
- **General/Task Creation** → GPT-4o (2500 tokens) - balanced for tasks

## Setup

### Prerequisites

- Python 3.12+ (required for telegram-bot compatibility)
- OpenAI API key with GPT-5 access
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Your Telegram User ID (get from [@userinfobot](https://t.me/userinfobot))

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd telegram-code-agent
```

2. **Create virtual environment**
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install python-telegram-bot==20.7 openai requests
```

4. **Configure the bot**

Edit `bot.py` and update these configuration values:

```python
TELEGRAM_TOKEN = "your-telegram-bot-token"
ALLOWED_USER_ID = your-telegram-user-id  # Get from @userinfobot
OPENAI_API_KEY = "your-openai-api-key"
REPO_PATH = "/path/to/your/codebase"  # Optional: for code discussions
```

5. **Run the bot**
```bash
python bot.py
```

The bot will start and you'll see: "August is online! 🎯"

## August's Personality

August is:
- **Strategic** - Thinks 3 steps ahead
- **Detail-oriented** - Nothing falls through cracks
- **Proactive** - Anticipates problems
- **Professional but warm** - Cares about team & product
- **Data-informed** - Loves metrics, balances with intuition
- **Decisive** - Makes calls quickly with clear rationale
- **Action-oriented** - Every conversation ends with next steps

## Database Schema

### Tasks Table
- `id` - Unique task ID (TASK-XXXXXXXX)
- `title` - Short task title
- `description` - Detailed description
- `agent` - Assigned agent ID
- `state` - Current workflow state
- `priority` - P0, P1, P2, or P3
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `parent_task` - For subtasks
- `tags` - JSON array

### Task History Table
- Audit trail of all task changes
- Tracks state transitions
- Records who/when/what changed

## Troubleshooting

### Python 3.13 Compatibility Issues

Use Python 3.12 instead:
```bash
python3.12 -m venv venv
```

### Telegram Markdown Errors

The bot automatically falls back to plain text if Markdown parsing fails.

### Vibe Sync Shows 0 Tasks

Make sure:
1. Vibe Kanban is running on `http://127.0.0.1:52822`
2. Project ID is correct in `vibe_sync.py`
3. API endpoint is accessible: `curl http://127.0.0.1:52822/api/projects`

### Bot Not Responding

Check:
1. Bot token is correct
2. User ID is correct (use @userinfobot on Telegram)
3. Bot process is running: `ps aux | grep bot.py`

## Customization

### Adjust August's Personality

Edit `august_prompt.py` to modify:
- Communication style (conversational vs formal)
- Decision-making approach (autonomous vs cautious)
- Task creation behavior (when to create vs discuss)
- Technical discussion depth

### Add New Agents

Edit `agents.py`:

```python
AGENTS["new_agent"] = Agent(
    id="new_agent",
    name="Agent Name",
    emoji="🔥",
    role="Role Description",
    expertise=["Skill 1", "Skill 2"],
    personality="Personality description"
)
```

### Modify Task States

Edit `task_manager.py` to add/modify states in the `TaskState` enum.

### Change Notification Settings

Edit `notifications.py` to adjust:
- Notification frequency (default: every 5 minutes)
- Daily summary time (default: 9:00 AM)
- Alert thresholds for blocked/stale tasks

## Security Notes

⚠️ **Never commit secrets to git!**

The `.gitignore` includes:
- API keys
- Database files (tasks.db)
- Virtual environment

For production use:
1. Use environment variables for secrets instead of hardcoding
2. Set up proper authentication
3. Run bot as a service (systemd, Docker, etc.)
4. Enable HTTPS for Vibe Kanban if exposed

## Contributing

Contributions are welcome! Feel free to:
- Add new agents
- Improve August's personality
- Add integrations (GitHub, Linear, Jira, etc.)
- Enhance notification system
- Improve natural language understanding

## License

MIT License - feel free to use and modify!

## Credits

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [OpenAI GPT-5](https://openai.com)
- [Vibe Kanban](https://vibekanban.com)

---

**Note**: This bot is designed for personal/team use. For production deployments with multiple users, add proper authentication, rate limiting, and error handling.
