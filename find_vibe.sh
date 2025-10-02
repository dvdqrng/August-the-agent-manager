#!/bin/bash

echo "🔍 Finding Vibe Kanban data storage..."
echo ""

# Check if Vibe is running
echo "1️⃣ Checking if Vibe Kanban is running..."
VIBE_PID=$(pgrep -f "vibe" | head -1)
if [ -n "$VIBE_PID" ]; then
    echo "   ✅ Vibe is running (PID: $VIBE_PID)"
    echo ""
    echo "2️⃣ Open files by Vibe process:"
    lsof -p $VIBE_PID 2>/dev/null | grep -E '\\.db|\\.json|\\.sqlite' | head -10
else
    echo "   ❌ Vibe Kanban not running on port 52822"
fi

echo ""
echo "3️⃣ Checking common data locations..."

# Check common app data locations
LOCATIONS=(
    "$HOME/.vibe-kanban"
    "$HOME/.local/share/vibe-kanban"
    "$HOME/Library/Application Support/vibe-kanban"
    "$HOME/Library/ApplicationSupport/vibe-kanban"
    "$HOME/.config/vibe-kanban"
)

for loc in "${LOCATIONS[@]}"; do
    if [ -d "$loc" ]; then
        echo "   ✅ Found: $loc"
        ls -la "$loc"
    fi
done

echo ""
echo "4️⃣ Recently modified DB/JSON files (last 30 min)..."
find ~ -name "*.db" -mmin -30 -not -path "*/Library/Caches/*" -not -path "*/.Trash/*" 2>/dev/null | head -10
find ~ -name "vibe*.json" -mmin -30 2>/dev/null | head -5

echo ""
echo "5️⃣ Checking if Vibe API is accessible..."
if command -v curl &> /dev/null; then
    echo "   Testing: http://127.0.0.1:52822/api/tasks"
    curl -s http://127.0.0.1:52822/api/tasks 2>&1 | head -5

    echo ""
    echo "   Testing: http://127.0.0.1:52822/api/projects"
    curl -s http://127.0.0.1:52822/api/projects 2>&1 | head -5
fi

echo ""
echo "6️⃣ Checking Lovemail repo for Vibe config..."
if [ -d "/Users/davidquiring/Documents/Documents - MacBook Pro von David/GitHub/lovemail/.vibe" ]; then
    echo "   ✅ Found .vibe directory in Lovemail repo!"
    ls -la "/Users/davidquiring/Documents/Documents - MacBook Pro von David/GitHub/lovemail/.vibe"
fi

echo ""
echo "✅ Diagnostic complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Share the output above"
echo "   2. Try creating a task in Vibe, then run this script again"
echo "   3. Check Vibe's settings/preferences for data location"
