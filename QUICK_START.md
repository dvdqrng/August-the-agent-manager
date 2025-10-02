# Quick Start - Use the Shared August Bot

Get started in 2 minutes! Use our shared bot instance - no bot setup needed.

## Option 1: Use the Shared Bot (Recommended - 2 minutes)

### Step 1: Get Your Telegram User ID

1. Open Telegram
2. Message [@userinfobot](https://t.me/userinfobot)
3. Copy your user ID (it's a number like `1126962381`)

### Step 2: Run the Setup Script

```bash
# Clone the repo
git clone https://github.com/yourname/august-pm-bot
cd august-pm-bot

# Run setup
python3 setup.py
```

The setup will ask you for:
- Your Telegram User ID
- Your codebase path (optional - for code discussions)
- Your project name
- Vibe Kanban setup (optional)
- Notification preferences

### Step 3: Share Your Config

Your config will be saved to `configs/user_YOUR_ID.json`

**Option A: If you're the bot host**
- Just run `python3 bot.py`
- Your config is already in place!

**Option B: If someone else hosts the bot**
- Share your `configs/user_YOUR_ID.json` file with them
- They'll add it to their `configs/` folder
- That's it!

### Step 4: Start Using August

1. Open Telegram
2. Message [@AugustPMBot](https://t.me/AugustPMBot) (or whatever the bot name is)
3. Send `/start`
4. Start chatting!

## Option 2: Run Your Own Bot Instance (10 minutes)

### Prerequisites

- Python 3.12+
- OpenAI API key with GPT-5 access
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Step 1: Create Your Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow the prompts to create your bot
4. Copy the bot token

### Step 2: Install

```bash
# Clone and setup
git clone https://github.com/yourname/august-pm-bot
cd august-pm-bot

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install python-telegram-bot==20.7 openai requests
```

### Step 3: Configure

Edit `bot.py` and update:

```python
TELEGRAM_TOKEN = "your-bot-token-from-botfather"
ALLOWED_USER_ID = your-telegram-user-id  # from @userinfobot
OPENAI_API_KEY = "your-openai-api-key"
REPO_PATH = "/path/to/your/codebase"  # optional
```

**Or use environment variables (recommended):**

```bash
export TELEGRAM_TOKEN="your-bot-token"
export OPENAI_API_KEY="your-openai-key"
```

### Step 4: Run

```bash
python3 bot.py
```

You'll see: `August is online! 🎯`

### Step 5: Use It

1. Open Telegram
2. Search for your bot (the name you gave BotFather)
3. Send `/start`
4. Start managing your workflow!

## What You Can Do

### Create Tasks
```
"Create a task to fix the email sync bug"
"We need to implement dark mode"
```

### Discuss Code
```
"What is the edge function doing?"
"How does authentication work?"
"Explain the caching strategy"
```

### Check Status
```
"What's in progress?"
"Show me blocked tasks"
"/standup"
```

### Sync with Vibe Kanban
```
/sync_vibe
```
Then click Import/Export buttons

## Examples

**Task Creation:**
> You: "Create a task to migrate to Vertex AI"
>
> August: ✅ Done! Created task for 💻 Engineer.
>
> **Vertex AI Migration** (TASK-ABC123)
> - Priority: 🔴 P0 (cost optimization)
> - Agent: Engineer
> - Status: 🆕 BACKLOG → moving to 📋 PLANNED

**Technical Discussion:**
> You: "Why do we need the edge function?"
>
> August: It's basically our backend API running on Supabase Edge.
>
> Main job? Keep API keys safe. Can't put them in the iOS app.
>
> The big endpoints:
> - /ai/generate - handles Gemini calls
> - /gmail/webhook - syncs inbox
>
> Plus it gives us logging and retry logic in one place.

**Status Check:**
> You: "/workload"
>
> August: **📊 Team Workload**
>
> 💻 Engineer: 3 tasks (2 in progress, 1 review)
> 🎨 Designer: 1 task (in progress)
> 🧪 QA: 2 tasks (both in review)

## Troubleshooting

**"Bot not responding"**
- Check bot is running: `ps aux | grep bot.py`
- Verify your User ID is correct
- Make sure config exists: `ls configs/user_*.json`

**"Can't find @AugustPMBot"**
- Ask the bot host for the correct bot username
- Or set up your own bot (Option 2 above)

**"Vibe sync shows 0 tasks"**
- Verify Vibe is running: `curl http://127.0.0.1:52822/api/projects`
- Check project ID in your config
- Make sure Vibe Kanban is actually running locally

## Next Steps

- Read the [full README](README.md) for advanced features
- Customize August's personality in `august_prompt.py`
- Add more agents in `agents.py`
- Check out [Vibe Kanban integration](VIBE_SETUP.md)
- Set up [proactive notifications](NOTIFICATIONS.md)

---

**Need help?** Open an issue on GitHub or ask August directly in Telegram!
