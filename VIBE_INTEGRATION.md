# August ↔️ Vibe Kanban Integration Plan

## Overview

Vibe Kanban is your local git-based kanban board. August needs to sync with it so both show the same agents and tasks.

## Architecture

```
Git Repository (Source of Truth)
    ↓
Vibe Kanban ← → August Bot
    ↑              ↓
  Local UI    Telegram
```

## Integration Strategy

Since Vibe Kanban stores data in a local database/git repository, we have several sync options:

### Option 1: **Vibe Kanban API Integration** (Best)

If Vibe exposes a REST API on localhost:

```python
# August syncs with Vibe
GET  http://127.0.0.1:52822/api/tasks
POST http://127.0.0.1:52822/api/tasks
PUT  http://127.0.0.1:52822/api/tasks/{id}
```

**Implementation:**
1. Add Vibe API client to August
2. `/sync` command pulls tasks from Vibe
3. When August creates tasks, POST to Vibe API
4. Polling every 5 minutes for updates

### Option 2: **Shared SQLite Database** (Fastest)

If Vibe uses SQLite:

```python
# Both apps point to same database
VIBE_DB = "/path/to/vibe/kanban.db"

# August reads/writes directly
# No HTTP overhead
# Real-time sync
```

**Implementation:**
1. Find Vibe's SQLite database location
2. Point August's TaskManager to same DB
3. Ensure schema compatibility
4. Add agent/state mappings

### Option 3: **Git-Based Sync** (Most Reliable)

If Vibe commits tasks to git:

```bash
# Vibe stores tasks as files
.vibe/
  agents/
    engineer.json
    designer.json
  tasks/
    TASK-123.json
    TASK-456.json
  columns/
    backlog.json
    in_progress.json
```

**Implementation:**
1. August writes tasks as JSON files
2. Git commits represent state changes
3. Both Vibe and August watch git for changes
4. File-based sync via git hooks

### Option 4: **Export/Import Scripts** (Simplest)

Manual sync via scripts:

```bash
# Export from Vibe
vibe export --format=json > tasks.json

# Import to August
august import tasks.json

# Export from August
august export > august_tasks.json

# Import to Vibe
vibe import august_tasks.json
```

## Recommended Approach

**I recommend Option 2 (Shared SQLite)** if possible because:
- Real-time sync
- No API overhead
- Simple implementation
- Git still tracks database changes

## Implementation Steps

1. **Locate Vibe's data storage**
   ```bash
   # Find where Vibe stores tasks
   lsof -p $(pgrep -f vibe-kanban) | grep -E '\\.db|\\.json'
   ```

2. **Analyze Vibe's schema**
   ```bash
   sqlite3 /path/to/vibe.db ".schema"
   ```

3. **Map Vibe ↔️ August entities**
   ```
   Vibe Agent    → August Agent
   Vibe Column   → August TaskState
   Vibe Task     → August Task
   Vibe Priority → August TaskPriority
   ```

4. **Create sync adapter**
   ```python
   class VibeAdapter:
       def sync_from_vibe():
           # Read Vibe tasks
           # Create/update August tasks

       def sync_to_vibe():
           # Read August tasks
           # Create/update Vibe tasks
   ```

5. **Add sync command**
   ```
   /sync - Sync with Vibe Kanban
   /sync_status - Show sync health
   ```

## Next Steps

To implement this, I need to know:

1. **Where does Vibe store data?**
   - Run: `lsof -p $(pgrep -f vibe)` and share output
   - Or: Open Vibe Kanban, create a task, then run:
     ```bash
     find ~ -name "*.db" -mmin -5
     find ~ -name "*.json" -mmin -5
     ```

2. **What's the project ID?**
   - From your URL: `04818b0a-f69b-42c0-858a-4c9132723523`
   - Is this stored in git or local DB?

3. **Can you export a task?**
   - Try: Vibe UI → Export → Share the JSON format

Once I have this info, I'll build the sync integration in ~30 minutes!

## Fallback: Manual Export/Import

If we can't auto-sync, I can create:

```bash
# Export August tasks to Vibe-compatible format
august export --format=vibe > vibe_tasks.json

# You import to Vibe manually
# Or vice versa
```

This is less elegant but gets the job done while we figure out the full integration.

---

**Ready to implement when you share:**
1. Vibe's data storage location
2. Sample task export from Vibe
3. Whether Vibe has an API endpoint
