import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from openai import OpenAI

# Import our modules
from agents import AGENTS, get_agent, format_agent_info, get_all_agents
from task_manager import TaskManager, TaskState, TaskPriority
from august_prompt import get_august_prompt
from vibe_sync import VibeKanbanClient, VibeAugustSync
from notifications import NotificationManager, NotificationScheduler

# ============= CONFIGURATION =============
# TODO: Move these to environment variables for security
TELEGRAM_TOKEN = "your-telegram-bot-token-here"
ALLOWED_USER_ID = 0  # Your Telegram user ID (get from @userinfobot)
OPENAI_API_KEY = "your-openai-api-key-here"
REPO_PATH = "/path/to/your/codebase"  # Optional: for technical discussions
# =========================================

openai_client = OpenAI(api_key=OPENAI_API_KEY)
task_manager = TaskManager()
vibe_sync = VibeAugustSync(task_manager)
notification_manager = None  # Initialized in main()


def check_auth(update: Update) -> bool:
    """Check if user is authorized"""
    return update.effective_user.id == ALLOWED_USER_ID


async def classify_message_intent(message: str) -> str:
    """
    Classify user message intent to route to appropriate handler
    Returns: "deep_technical", "task_creation", "task_status", or "general"
    """
    message_lower = message.lower()

    # Technical discussion indicators - questions about code/architecture
    technical_keywords = [
        "what is", "what does", "how does", "why do we", "why does",
        "explain", "tell me about", "look into", "dive into",
        "architecture", "implementation", "function", "class", "method",
        "edge function", "api", "database", "supabase", "swiftui",
        "how is", "how are", "where is", "can you explain"
    ]

    # Task creation indicators - explicit work requests
    task_creation_keywords = [
        "create a task", "add a task", "create task", "add task",
        "we need to implement", "we need to fix", "we need to add",
        "let's implement", "let's fix", "let's add",
        "kick off", "start work on"
    ]

    # Task status indicators
    status_keywords = [
        "what's in progress", "current tasks", "task status",
        "what are we working on", "show tasks", "what's the team",
        "standup", "sprint", "what's blocked"
    ]

    # Check for task creation first (most explicit)
    if any(keyword in message_lower for keyword in task_creation_keywords):
        return "task_creation"

    # Check for status requests
    if any(keyword in message_lower for keyword in status_keywords):
        return "task_status"

    # Check for technical discussion
    if any(keyword in message_lower for keyword in technical_keywords):
        return "deep_technical"

    # Default to general
    return "general"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not check_auth(update):
        await update.message.reply_text("Unauthorized")
        return

    welcome_msg = """🎯 **Hey! I'm August, your AI Product Manager**

I coordinate the Lovemail development team and manage our workflow.

**What I can do:**

📋 **Task Management**
• Create tasks: "Create a task to fix email sync"
• Check status: "What's in progress?"
• Update tasks: "Move TASK-ABC to review"

👥 **Team Coordination**
• See agents: `/agents`
• Check workload: `/workload`
• Daily standup: `/standup`

🔔 **Proactive Updates** (NEW!)
• I'll notify you when tasks change state
• Daily summaries at 9 AM
• Alerts for blocked or stale P0 tasks
• Celebrations when tasks complete 🎉

🔗 **Integrations**
• Vibe Kanban sync: `/sync_vibe`

💬 **General Chat**
• Ask questions about Lovemail
• Discuss priorities
• Plan sprints

**Quick Tips:**
• I'm decisive and take ownership - I'll create tasks immediately
• I send proactive updates so you stay in the loop
• Mention agent emojis to assign work (e.g., "💻 Engineer")

Ready to ship something great? What do you need?"""

    # Add quick action buttons
    keyboard = [
        [
            InlineKeyboardButton("📋 View Tasks", callback_data="cmd_tasks"),
            InlineKeyboardButton("👥 Team", callback_data="cmd_agents"),
        ],
        [
            InlineKeyboardButton("📊 Workload", callback_data="cmd_workload"),
            InlineKeyboardButton("☕ Standup", callback_data="cmd_standup"),
        ],
        [
            InlineKeyboardButton("🔄 Sync Vibe", callback_data="cmd_sync_vibe"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_msg, parse_mode='Markdown', reply_markup=reply_markup)


async def agents_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all agents"""
    if not check_auth(update):
        return

    agents = get_all_agents()
    msg = "**🎯 Your Development Team**\n\n"

    for agent in agents:
        msg += f"{format_agent_info(agent)}\n\n"

    await update.message.reply_text(msg, parse_mode='Markdown')


async def workload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show workload per agent"""
    if not check_auth(update):
        return

    workload = task_manager.get_workload_summary()
    msg = "**📊 Team Workload** (active tasks)\n\n"

    if not workload:
        msg += "No active tasks right now. Clean slate!"
    else:
        for agent_id, count in sorted(workload.items(), key=lambda x: x[1], reverse=True):
            agent = get_agent(agent_id)
            if agent:
                msg += f"{agent.emoji} **{agent.name}**: {count} tasks\n"

    await update.message.reply_text(msg, parse_mode='Markdown')


async def standup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate daily standup"""
    if not check_auth(update):
        return

    await update.message.reply_text("Generating standup report...")

    # Get tasks by state
    in_progress = task_manager.get_tasks_by_state(TaskState.IN_PROGRESS)
    in_review = task_manager.get_tasks_by_state(TaskState.REVIEW)
    blocked = task_manager.get_tasks_by_state(TaskState.BLOCKED)

    msg = "**🎯 Daily Standup**\n\n"

    if in_progress:
        msg += "**🏃 In Progress** (" + str(len(in_progress)) + ")\n"
        for task in in_progress[:5]:
            msg += f"• {task.title} ({task.agent})\n"
        msg += "\n"

    if in_review:
        msg += "**👀 In Review** (" + str(len(in_review)) + ")\n"
        for task in in_review[:5]:
            msg += f"• {task.title} ({task.agent})\n"
        msg += "\n"

    if blocked:
        msg += "**❌ Blocked** (" + str(len(blocked)) + ")\n"
        for task in blocked[:5]:
            msg += f"• {task.title} ({task.agent})\n"
        msg += "\n"

    if not in_progress and not in_review and not blocked:
        msg += "All clear! No active work right now."

    await update.message.reply_text(msg, parse_mode='Markdown')


async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all tasks"""
    if not check_auth(update):
        return

    args = context.args
    if args and args[0] in ['backlog', 'planned', 'progress', 'review', 'done', 'blocked']:
        state_map = {
            'backlog': TaskState.BACKLOG,
            'planned': TaskState.PLANNED,
            'progress': TaskState.IN_PROGRESS,
            'review': TaskState.REVIEW,
            'done': TaskState.DONE,
            'blocked': TaskState.BLOCKED
        }
        tasks = task_manager.get_tasks_by_state(state_map[args[0]])
        state_name = args[0].upper()
    else:
        tasks = task_manager.get_all_tasks()
        state_name = "ALL"

    if not tasks:
        await update.message.reply_text(f"No {state_name} tasks found.")
        return

    msg = f"**📋 Tasks ({state_name})** ({len(tasks)} total)\n\n"

    for task in tasks[:10]:
        msg += f"{task.state.emoji} {task.priority.emoji} **{task.title}**\n"
        msg += f"   Agent: {task.agent} • {task.id}\n\n"

    if len(tasks) > 10:
        msg += f"\n_Showing 10 of {len(tasks)} tasks. Use /tasks <state> to filter._"

    await update.message.reply_text(msg, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages - route to August"""
    if not check_auth(update):
        return

    user_message = update.message.text

    # Classify the intent of the message
    intent = await classify_message_intent(user_message)

    # Build context for August
    recent_tasks = task_manager.get_all_tasks()[:10]
    tasks_context = "\n".join([
        f"- {t.id}: {t.title} ({t.agent}, {t.state.display_name})"
        for t in recent_tasks
    ]) if recent_tasks else "No tasks yet"

    # Build the prompt for August
    system_prompt = get_august_prompt()

    # Determine model and token limits based on intent
    if intent == "deep_technical":
        model = "gpt-5-2025-08-07"  # Use GPT-5 for deep technical analysis
        max_tokens = 4000
    elif intent == "task_status":
        model = "gpt-4o-mini"  # Fast and efficient for status
        max_tokens = 1500
    else:  # task_creation or general
        model = "gpt-4o"  # Balanced for general tasks
        max_tokens = 2500

    context_prompt = f"""
CURRENT CONTEXT:

Recent Tasks:
{tasks_context}

Available Agents: {', '.join([a.emoji + ' ' + a.name for a in get_all_agents()])}

Repository Path: {REPO_PATH}

---

USER MESSAGE:
{user_message}

---

MESSAGE INTENT: {intent}

INSTRUCTIONS FOR YOUR RESPONSE:

**If the user wants to create a task (explicit request like "create task", "add task", "we need to implement"):**
1. Make decisions about title, agent, priority yourself
2. Respond with EXACTLY this format at the start of your message:
   TASK_CREATE: title | agent_emoji | priority

   Example: TASK_CREATE: Fix email sync bug | 💻 | P0

3. Then explain your reasoning

**If the user asks for task status or overview:**
- Provide clear, concise summary
- Use task data from context above
- NO code analysis needed

**If the user asks about code/architecture/implementation ("what is X doing", "how does Y work", "can you look into Z"):**
- This is a TECHNICAL DISCUSSION, not task management
- NO task creation! Just answer the technical question
- SPLIT your response using "---" to create separate messages (like texting)
- Keep each message 2-3 sentences max
- Use casual language: "checks if user is legit" not "validates authentication credentials"
- Get to the point - no fluff

**General:**
- Be decisive and take ownership
- Don't ask unnecessary clarifying questions
- Format in Telegram-friendly Markdown
- NO "thinking" statements - just share your insight directly
- Talk like texting a friend - short, punchy messages split with "---"
- Remember: You're the PM. Act like it!
"""

    try:
        # GPT-5 has restrictions: no temperature, no max_tokens
        if "gpt-5" in model:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_prompt}
                ]
            )
        else:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )

        august_response = response.choices[0].message.content.strip()

        # Check if August wants to create a task
        if august_response.startswith("TASK_CREATE:"):
            lines = august_response.split('\n')
            task_line = lines[0].replace("TASK_CREATE:", "").strip()
            parts = [p.strip() for p in task_line.split('|')]

            if len(parts) >= 3:
                task_title = parts[0]
                agent_emoji = parts[1]
                priority_str = parts[2]

                # Map emoji to agent
                agent_map = {agent.emoji: agent.id for agent in get_all_agents()}
                agent_id = agent_map.get(agent_emoji, 'engineer')

                # Map priority
                priority_map = {
                    'P0': TaskPriority.P0,
                    'P1': TaskPriority.P1,
                    'P2': TaskPriority.P2,
                    'P3': TaskPriority.P3
                }
                priority = priority_map.get(priority_str, TaskPriority.P2)

                # Create the task
                task = task_manager.create_task(
                    title=task_title,
                    description=user_message,
                    agent=agent_id,
                    priority=priority
                )

                # Send August's explanation with task ID
                explanation = '\n'.join(lines[1:]).strip()
                agent = get_agent(agent_id)

                full_response = f"✅ **Task Created: {task.id}**\n\n"
                full_response += f"{task.state.emoji} {task.priority.emoji} **{task.title}**\n"
                full_response += f"Assigned to: {agent.emoji} {agent.name}\n\n"
                full_response += explanation

                await update.message.reply_text(full_response, parse_mode='Markdown')
                return

        # Split response into multiple messages if August used "---"
        messages = august_response.split('---')

        for msg in messages:
            msg = msg.strip()
            if not msg:
                continue

            # Send each message separately with a small delay
            try:
                await update.message.reply_text(msg, parse_mode='Markdown')
            except Exception:
                # If Markdown parsing fails, send as plain text
                await update.message.reply_text(msg)

            # Small delay between messages to feel more human
            if len(messages) > 1:
                await asyncio.sleep(0.5)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button callbacks"""
    query = update.callback_query
    await query.answer()

    if not check_auth(update):
        return

    # Route to appropriate command based on callback data
    callback_data = query.data

    if callback_data == "cmd_tasks":
        await _tasks_response(query)
    elif callback_data == "cmd_agents":
        await _agents_response(query)
    elif callback_data == "cmd_workload":
        await _workload_response(query)
    elif callback_data == "cmd_standup":
        await _standup_response(query)
    elif callback_data == "cmd_sync_vibe":
        await _sync_vibe_response(query)
    elif callback_data == "sync_from_vibe":
        await _sync_from_vibe_callback(query)
    elif callback_data == "sync_to_vibe":
        await _sync_to_vibe_callback(query)


async def _tasks_response(query):
    """Show tasks via callback"""
    tasks = task_manager.get_all_tasks()

    if not tasks:
        await query.edit_message_text("No tasks found.")
        return

    msg = f"**📋 All Tasks** ({len(tasks)} total)\n\n"

    for task in tasks[:10]:
        msg += f"{task.state.emoji} {task.priority.emoji} **{task.title}**\n"
        msg += f"   Agent: {task.agent} • {task.id}\n\n"

    if len(tasks) > 10:
        msg += f"\n_Showing 10 of {len(tasks)} tasks._"

    # Add filter buttons
    keyboard = [
        [
            InlineKeyboardButton("🆕 Backlog", callback_data="filter_backlog"),
            InlineKeyboardButton("🏃 In Progress", callback_data="filter_progress"),
        ],
        [
            InlineKeyboardButton("👀 Review", callback_data="filter_review"),
            InlineKeyboardButton("✅ Done", callback_data="filter_done"),
        ],
        [InlineKeyboardButton("« Back", callback_data="back_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


async def _agents_response(query):
    """Show agents via callback"""
    agents = get_all_agents()
    msg = "**🎯 Your Development Team**\n\n"

    for agent in agents:
        msg += f"{format_agent_info(agent)}\n\n"

    keyboard = [[InlineKeyboardButton("« Back", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


async def _workload_response(query):
    """Show workload via callback"""
    workload = task_manager.get_workload_summary()
    msg = "**📊 Team Workload** (active tasks)\n\n"

    if not workload:
        msg += "No active tasks right now. Clean slate!"
    else:
        for agent_id, count in sorted(workload.items(), key=lambda x: x[1], reverse=True):
            agent = get_agent(agent_id)
            if agent:
                msg += f"{agent.emoji} **{agent.name}**: {count} tasks\n"

    keyboard = [[InlineKeyboardButton("« Back", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


async def _standup_response(query):
    """Show standup via callback"""
    in_progress = task_manager.get_tasks_by_state(TaskState.IN_PROGRESS)
    in_review = task_manager.get_tasks_by_state(TaskState.REVIEW)
    blocked = task_manager.get_tasks_by_state(TaskState.BLOCKED)

    msg = "**🎯 Daily Standup**\n\n"

    if in_progress:
        msg += "**🏃 In Progress** (" + str(len(in_progress)) + ")\n"
        for task in in_progress[:5]:
            msg += f"• {task.title} ({task.agent})\n"
        msg += "\n"

    if in_review:
        msg += "**👀 In Review** (" + str(len(in_review)) + ")\n"
        for task in in_review[:5]:
            msg += f"• {task.title} ({task.agent})\n"
        msg += "\n"

    if blocked:
        msg += "**❌ Blocked** (" + str(len(blocked)) + ")\n"
        for task in blocked[:5]:
            msg += f"• {task.title} ({task.agent})\n"
        msg += "\n"

    if not in_progress and not in_review and not blocked:
        msg += "All clear! No active work right now."

    keyboard = [[InlineKeyboardButton("« Back", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


async def _sync_vibe_response(query):
    """Show Vibe sync status via callback"""
    status = vibe_sync.get_sync_status()

    if not status.get("vibe_online"):
        msg = "❌ **Vibe Kanban Offline**\n\nMake sure Vibe is running."
        keyboard = [[InlineKeyboardButton("« Back", callback_data="back_main")]]
    else:
        msg = f"""✅ **Vibe Kanban Connected!**

📊 Status:
• Vibe tasks: {status['vibe_tasks']}
• August tasks: {status['august_tasks']}
• Projects: {len(status['projects'])}

Ready to sync!"""
        keyboard = [
            [InlineKeyboardButton("⬇️ Import from Vibe", callback_data="sync_from_vibe")],
            [InlineKeyboardButton("⬆️ Export to Vibe", callback_data="sync_to_vibe")],
            [InlineKeyboardButton("« Back", callback_data="back_main")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


async def _sync_from_vibe_callback(query):
    """Handle Import from Vibe button"""
    await query.answer("⬇️ Importing tasks...")

    try:
        stats = vibe_sync.sync_from_vibe()

        msg = f"""✅ **Import Complete!**

📊 Results:
• Fetched: {stats['fetched']} tasks
• Created: {stats['created']} new tasks
• Skipped: {stats['skipped']} (already exist)
• Errors: {stats['errors']}

Run /tasks to see all imported tasks!"""

        keyboard = [[InlineKeyboardButton("« Back to Sync", callback_data="cmd_sync_vibe")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
        await query.edit_message_text(f"❌ Import failed: {str(e)}")


async def _sync_to_vibe_callback(query):
    """Handle Export to Vibe button"""
    await query.answer("⬆️ Exporting tasks...")

    try:
        stats = vibe_sync.sync_to_vibe()

        msg = f"""✅ **Export Complete!**

📊 Results:
• Fetched: {stats['fetched']} August tasks
• Pushed: {stats['pushed']} to Vibe
• Errors: {stats['errors']}"""

        keyboard = [[InlineKeyboardButton("« Back to Sync", callback_data="cmd_sync_vibe")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

    except Exception as e:
        await query.edit_message_text(f"❌ Export failed: {str(e)}")


async def sync_vibe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sync with Vibe Kanban"""
    if not check_auth(update):
        return

    await update.message.reply_text("🔄 Checking Vibe Kanban connection...")

    # Get sync status
    status = vibe_sync.get_sync_status()

    if not status.get("vibe_online"):
        await update.message.reply_text(
            "❌ **Vibe Kanban Offline**\n\n"
            "Make sure Vibe is running at http://127.0.0.1:52822\n\n"
            f"Error: {status.get('error', 'Unknown')}"
        , parse_mode='Markdown')
        return

    msg = f"""✅ **Vibe Kanban Connected!**

📊 Status:
• Vibe tasks: {status['vibe_tasks']}
• August tasks: {status['august_tasks']}
• Projects: {len(status['projects'])}

Ready to sync!"""

    # Add sync buttons
    keyboard = [
        [InlineKeyboardButton("⬇️ Import from Vibe", callback_data="sync_from_vibe")],
        [InlineKeyboardButton("⬆️ Export to Vibe", callback_data="sync_to_vibe")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)


async def sync_from_vibe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Import tasks from Vibe to August"""
    if not check_auth(update):
        return

    await update.message.reply_text("⬇️ Importing tasks from Vibe Kanban...")

    try:
        stats = vibe_sync.sync_from_vibe()

        msg = f"""✅ **Import Complete!**

📊 Results:
• Fetched: {stats['fetched']} tasks
• Created: {stats['created']} new tasks
• Skipped: {stats['skipped']} (already exist)
• Errors: {stats['errors']}

Run `/tasks` to see all imported tasks!"""

        await update.message.reply_text(msg, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Import failed: {str(e)}")


async def create_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a new task"""
    if not check_auth(update):
        return

    # Get task details from arguments
    args = ' '.join(context.args) if context.args else ""

    if not args:
        await update.message.reply_text(
            "Usage: /create_task <task description>\n\n"
            "Example: /create_task Fix email sync bug - affects all users"
        )
        return

    # Create task with August's help
    await update.message.reply_text("Creating task with August's input...")

    system_prompt = """You are August, the PM. The user wants to create a task.
Extract: title (short), description, suggested agent emoji, priority level.

Respond in this format:
TITLE: <short title>
DESCRIPTION: <details>
AGENT: <emoji>
PRIORITY: <P0|P1|P2|P3>
"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create task: {args}"}
        ],
        temperature=0.3
    )

    # Parse response
    lines = response.choices[0].message.content.strip().split('\n')
    task_data = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            task_data[key.strip().upper()] = value.strip()

    # Map emoji to agent
    agent_map = {agent.emoji: agent.id for agent in get_all_agents()}
    agent_emoji = task_data.get('AGENT', '💻')
    agent_id = agent_map.get(agent_emoji, 'engineer')

    # Map priority
    priority_map = {
        'P0': TaskPriority.P0,
        'P1': TaskPriority.P1,
        'P2': TaskPriority.P2,
        'P3': TaskPriority.P3
    }
    priority = priority_map.get(task_data.get('PRIORITY', 'P2'), TaskPriority.P2)

    # Create the task
    task = task_manager.create_task(
        title=task_data.get('TITLE', args[:50]),
        description=task_data.get('DESCRIPTION', args),
        agent=agent_id,
        priority=priority
    )

    agent = get_agent(agent_id)
    msg = f"""✅ **Task Created!**

{task.format_display()}

Task ID: `{task.id}`

{agent.emoji} I've assigned this to **{agent.name}** based on the work type.
The task is in 🆕 BACKLOG. Ready to move to 📋 PLANNED?"""

    await update.message.reply_text(msg, parse_mode='Markdown')


async def start_notification_scheduler(application):
    """Start the background notification scheduler"""
    global notification_manager

    # Initialize notification manager
    notification_manager = NotificationManager(
        bot_token=TELEGRAM_TOKEN,
        user_id=ALLOWED_USER_ID,
        task_manager=task_manager
    )

    # Create and start scheduler
    scheduler = NotificationScheduler(notification_manager)

    # Run scheduler in background
    import asyncio
    asyncio.create_task(scheduler.start())

    print("🔔 Notification system started")
    print("   - Task state change alerts: ON")
    print("   - Daily summaries: 9:00 AM")
    print("   - Standup reminders: 9:30 AM")
    print("   - Blocked task alerts: ON")


def main():
    """Start the bot"""
    print("🎯 Starting August - AI Product Manager Bot...")
    print(f"📁 Repository: {REPO_PATH}")
    print(f"🔒 Authorized user: {ALLOWED_USER_ID}")
    print(f"👥 Team: {len(AGENTS)} agents")

    # Count tasks
    all_tasks = task_manager.get_all_tasks()
    print(f"📋 Tasks in system: {len(all_tasks)}")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("agents", agents_command))
    app.add_handler(CommandHandler("workload", workload_command))
    app.add_handler(CommandHandler("standup", standup_command))
    app.add_handler(CommandHandler("tasks", tasks_command))
    app.add_handler(CommandHandler("create_task", create_task_command))
    app.add_handler(CommandHandler("sync_vibe", sync_vibe_command))

    # Callback query handler for inline keyboards
    app.add_handler(CallbackQueryHandler(button_callback))

    # Message handler (August's conversational interface)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start notification scheduler
    app.post_init = start_notification_scheduler

    print("✅ August is online! Ready to coordinate the team.")
    app.run_polling()


if __name__ == '__main__':
    main()
