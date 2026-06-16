#!/bin/bash
"""
============================================
MyToolsTown Server Bot - Free Server Setup
============================================
Run this on any Linux server (Ubuntu 20.04+):
bash setup_free_server.sh

Works on:
- Oracle Cloud Free Tier (always free, best!)
- Google Cloud $300 trial
- AWS Free Tier
- Any VPS with Ubuntu
============================================
"""

echo "============================================"
echo "MyToolsTown Bot - Free Server Setup"
echo "============================================"
echo ""

# 1. Update system
echo "[1/6] Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

# 2. Install Python
echo "[2/6] Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git

# 3. Install Playwright dependencies
echo "[3/6] Installing Playwright browser dependencies..."
sudo apt install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    libatspi2.0-0

# 4. Install Python packages
echo "[4/6] Installing Python packages..."
pip3 install playwright
python3 -m playwright install chromium

# 5. Create bot directory
echo "[5/6] Setting up bot..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Make config.json if not exists
if [ ! -f config.json ]; then
    cat > config.json << 'CONFIGEOF'
{
    "instagram_username": "YOUR_USERNAME_HERE",
    "headless": true,
    "slow_mo": 100,
    "max_earn_cycles": 0,
    "verify_wait_time": 3,
    "cookies_file": "server_session.json",
    "cycle_delay_min": 25,
    "cycle_delay_max": 50,
    "long_break_interval": 8,
    "long_break_min": 120,
    "long_break_max": 240
}
CONFIGEOF
    echo "⚠️  Edit config.json and set your Instagram username!"
fi

# 6. Create systemd service (auto-start on boot)
echo "[6/6] Creating auto-start service..."
cat > mytoolstown-bot.service << 'SERVICEEOF'
[Unit]
Description=MyToolsTown Auto Credit Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/bot
ExecStart=/usr/bin/python3 /root/bot/server_bot.py
Restart=always
RestartSec=30
StandardOutput=append:/root/bot/server_bot.log
StandardError=append:/root/bot/server_bot.log

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo ""
echo "============================================"
echo "✅ Setup Complete!"
echo "============================================"
echo ""
echo "📝 Next steps:"
echo "1. Edit config.json:"
echo "   nano config.json"
echo "   (Set your Instagram username)"
echo ""
echo "2. Test the bot:"
echo "   python3 server_bot.py"
echo ""
echo "3. Install as service (auto-start on boot):"
echo "   sudo cp mytoolstown-bot.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable mytoolstown-bot"
echo "   sudo systemctl start mytoolstown-bot"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status mytoolstown-bot"
echo ""
echo "5. View logs:"
echo "   tail -f server_bot.log"
echo "============================================"