"""
Proactive notification system for August
Sends updates about task state changes and agent activity
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from telegram import Bot
from task_manager import TaskManager, TaskState, Task
from agents import get_agent
import json


class NotificationManager:
    """Manages proactive notifications for task and agent updates"""

    def __init__(self, bot_token: str, user_id: int, task_manager: TaskManager):
        self.bot = Bot(token=bot_token)
        self.user_id = user_id
        self.task_manager = task_manager
        self.last_check = datetime.now()
        self.notification_prefs = self._load_preferences()

    def _load_preferences(self) -> Dict:
        """Load user notification preferences"""
        # Default preferences
        return {
            "task_state_changes": True,
            "daily_summary": True,
            "daily_summary_time": "09:00",
            "weekly_summary": True,
            "weekly_summary_day": "monday",
            "agent_blocked_alerts": True,
            "p0_task_alerts": True,
            "task_completed_celebration": True,
            "standup_reminder": True,
            "standup_time": "09:30",
        }

    async def check_and_notify(self):
        """Check for changes and send notifications"""
        try:
            # Check for task state changes since last check
            await self._check_task_state_changes()

            # Check for blocked tasks
            await self._check_blocked_tasks()

            # Check for P0 tasks needing attention
            await self._check_p0_tasks()

            # Update last check time
            self.last_check = datetime.now()

        except Exception as e:
            print(f"Notification error: {e}")

    async def _check_task_state_changes(self):
        """Detect and notify about task state changes"""
        if not self.notification_prefs.get("task_state_changes"):
            return

        # Get recently updated tasks (last 5 minutes)
        all_tasks = self.task_manager.get_all_tasks()
        recent_updates = [
            t for t in all_tasks
            if (datetime.now() - t.updated_at).total_seconds() < 300
        ]

        for task in recent_updates:
            # Skip if we already notified about this
            if task.updated_at <= self.last_check:
                continue

            agent = get_agent(task.agent)
            msg = self._format_task_update(task, agent.emoji if agent else "🤖")
            await self.send_notification(msg)

    async def _check_blocked_tasks(self):
        """Alert when tasks become blocked"""
        if not self.notification_prefs.get("agent_blocked_alerts"):
            return

        blocked_tasks = self.task_manager.get_tasks_by_state(TaskState.BLOCKED)

        # Only alert on newly blocked tasks
        newly_blocked = [
            t for t in blocked_tasks
            if (datetime.now() - t.updated_at).total_seconds() < 300
            and t.updated_at > self.last_check
        ]

        if newly_blocked:
            msg = f"🚨 **{len(newly_blocked)} Task(s) Blocked!**\n\n"
            for task in newly_blocked[:3]:
                agent = get_agent(task.agent)
                msg += f"❌ {task.title}\n"
                msg += f"   Agent: {agent.emoji if agent else '🤖'} {task.agent}\n\n"

            msg += "These need your attention to unblock!"
            await self.send_notification(msg)

    async def _check_p0_tasks(self):
        """Alert about P0 tasks needing attention"""
        if not self.notification_prefs.get("p0_task_alerts"):
            return

        all_tasks = self.task_manager.get_all_tasks()
        p0_in_progress = [
            t for t in all_tasks
            if t.priority.name == "P0" and t.state == TaskState.IN_PROGRESS
        ]

        # Alert if P0 tasks have been in progress for >24 hours
        stale_p0 = [
            t for t in p0_in_progress
            if (datetime.now() - t.updated_at).total_seconds() > 86400
        ]

        if stale_p0:
            msg = f"⏰ **P0 Task Alert**\n\n"
            msg += f"{len(stale_p0)} critical task(s) in progress >24h:\n\n"
            for task in stale_p0[:3]:
                agent = get_agent(task.agent)
                msg += f"🔴 {task.title}\n"
                msg += f"   {agent.emoji if agent else '🤖'} {task.agent}\n\n"

            msg += "Should we check on progress or escalate?"
            await self.send_notification(msg)

    def _format_task_update(self, task: Task, agent_emoji: str) -> str:
        """Format a task state change notification"""
        return (
            f"{task.state.emoji} **Task Updated**\n\n"
            f"{task.priority.emoji} {task.title}\n"
            f"Agent: {agent_emoji} {task.agent}\n"
            f"Status: {task.state.display_name}\n\n"
            f"ID: `{task.id}`"
        )

    async def send_notification(self, message: str):
        """Send a notification to the user"""
        try:
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Failed to send notification: {e}")

    async def send_daily_summary(self):
        """Send daily summary of team activity"""
        if not self.notification_prefs.get("daily_summary"):
            return

        in_progress = self.task_manager.get_tasks_by_state(TaskState.IN_PROGRESS)
        in_review = self.task_manager.get_tasks_by_state(TaskState.REVIEW)
        blocked = self.task_manager.get_tasks_by_state(TaskState.BLOCKED)

        msg = f"🌅 **Daily Summary - {datetime.now().strftime('%B %d, %Y')}**\n\n"

        if in_progress:
            msg += f"**🏃 In Progress** ({len(in_progress)})\n"
            for task in in_progress[:5]:
                agent = get_agent(task.agent)
                msg += f"• {task.title} ({agent.emoji if agent else '🤖'})\n"
            msg += "\n"

        if in_review:
            msg += f"**👀 In Review** ({len(in_review)})\n"
            for task in in_review[:5]:
                agent = get_agent(task.agent)
                msg += f"• {task.title} ({agent.emoji if agent else '🤖'})\n"
            msg += "\n"

        if blocked:
            msg += f"**❌ Blocked** ({len(blocked)})\n"
            for task in blocked[:3]:
                agent = get_agent(task.agent)
                msg += f"• {task.title} ({agent.emoji if agent else '🤖'})\n"
            msg += "\n"

        if not in_progress and not in_review and not blocked:
            msg += "All clear! No active work right now.\n\n"

        msg += "Have a productive day! 🚀"

        await self.send_notification(msg)

    async def send_task_completed_celebration(self, task: Task):
        """Celebrate when a task is completed"""
        if not self.notification_prefs.get("task_completed_celebration"):
            return

        agent = get_agent(task.agent)
        msg = (
            f"🎉 **Task Completed!**\n\n"
            f"✅ {task.title}\n"
            f"Agent: {agent.emoji if agent else '🤖'} {agent.name if agent else task.agent}\n\n"
            f"Great work! Keep the momentum going!"
        )

        await self.send_notification(msg)

    async def send_standup_reminder(self):
        """Send standup reminder"""
        if not self.notification_prefs.get("standup_reminder"):
            return

        msg = (
            "☕ **Good morning!**\n\n"
            "Ready for today's standup?\n\n"
            "Send `/standup` to see what the team is working on."
        )

        await self.send_notification(msg)


class NotificationScheduler:
    """Schedules periodic notifications"""

    def __init__(self, notification_manager: NotificationManager):
        self.notification_manager = notification_manager
        self.running = False

    async def start(self):
        """Start the notification scheduler"""
        self.running = True

        # Run periodic checks
        while self.running:
            try:
                # Check every 5 minutes for state changes
                await self.notification_manager.check_and_notify()

                # Check if it's time for daily summary
                await self._check_daily_summary()

                # Check if it's time for standup reminder
                await self._check_standup_reminder()

                # Wait 5 minutes before next check
                await asyncio.sleep(300)

            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(60)

    async def _check_daily_summary(self):
        """Check if it's time for daily summary"""
        prefs = self.notification_manager.notification_prefs
        summary_time = prefs.get("daily_summary_time", "09:00")

        now = datetime.now()
        target_time = datetime.strptime(summary_time, "%H:%M").time()

        # Send if current time matches target (within 5 min window)
        if abs((now.time().hour * 60 + now.time().minute) -
               (target_time.hour * 60 + target_time.minute)) <= 5:
            await self.notification_manager.send_daily_summary()

    async def _check_standup_reminder(self):
        """Check if it's time for standup reminder"""
        prefs = self.notification_manager.notification_prefs
        standup_time = prefs.get("standup_time", "09:30")

        now = datetime.now()
        target_time = datetime.strptime(standup_time, "%H:%M").time()

        if abs((now.time().hour * 60 + now.time().minute) -
               (target_time.hour * 60 + target_time.minute)) <= 5:
            await self.notification_manager.send_standup_reminder()

    def stop(self):
        """Stop the scheduler"""
        self.running = False
