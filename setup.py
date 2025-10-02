#!/usr/bin/env python3
"""
Quick setup script for August bot
Creates user configuration to connect to shared bot instance
"""

import json
import os
import sys
from pathlib import Path

def setup():
    print("🎯 Welcome to August Setup!\n")
    print("This will configure your personal August workspace.")
    print("You'll use a shared bot instance - no bot setup needed!\n")

    # Get Telegram User ID
    print("1️⃣  Your Telegram User ID")
    print("   → Open Telegram and message @userinfobot")
    print("   → Copy your user ID\n")
    telegram_user_id = input("   Your Telegram User ID: ").strip()

    if not telegram_user_id.isdigit():
        print("❌ Invalid user ID. Please enter a number.")
        return

    user_id = int(telegram_user_id)

    # Create configs directory
    configs_dir = Path("configs")
    configs_dir.mkdir(exist_ok=True)

    config_file = configs_dir / f"user_{user_id}.json"

    # Check if config already exists
    if config_file.exists():
        print(f"\n⚠️  Configuration already exists for user {user_id}!")
        overwrite = input("   Do you want to overwrite it? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return

    # Get repository path
    print("\n2️⃣  Repository Path (optional)")
    print("   → This allows August to discuss your code")
    print("   → Leave empty to skip\n")
    repo_path = input("   Your codebase path: ").strip()

    # Get project name
    print("\n3️⃣  Project Name")
    project_name = input("   Your project name (e.g., MyApp): ").strip() or "MyProject"

    # Vibe Kanban setup
    print("\n4️⃣  Vibe Kanban Integration (optional)")
    vibe_enabled = input("   Do you use Vibe Kanban locally? (y/N): ").lower() == 'y'

    vibe_config = {
        "enabled": vibe_enabled,
        "url": "http://127.0.0.1:52822",
        "project_id": ""
    }

    if vibe_enabled:
        print("\n   → Make sure Vibe Kanban is running locally")
        project_id = input("   Vibe Project ID: ").strip()
        vibe_config["project_id"] = project_id

    # Notifications
    print("\n5️⃣  Notifications")
    notifications_enabled = input("   Enable daily summaries? (Y/n): ").lower() != 'n'
    daily_time = input("   Daily summary time (default: 09:00): ").strip() or "09:00"
    standup = input("   Enable standup reminders? (Y/n): ").lower() != 'n'

    # Create config
    config = {
        "telegram_user_id": user_id,
        "repo_path": repo_path,
        "project_name": project_name,
        "vibe_kanban": vibe_config,
        "notifications": {
            "enabled": notifications_enabled,
            "daily_summary_time": daily_time,
            "standup_reminder": standup
        }
    }

    # Save config
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuration saved to {config_file}!")
    print("\n📋 Next steps:")
    print("   1. Share this configs/ folder with the bot host")
    print("   2. Or, if you're running the bot: start bot.py")
    print("   3. Message @AugustPMBot on Telegram")
    print("   4. Send /start to begin")
    print("\n🎯 August is ready to manage your workflow!")

if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
