#!/bin/bash
# Setup script for Oracle Cloud Free Tier VM
# Run this after cloning your repo

BOT_DIR="$HOME/evony-shield-watch"
SERVICE_NAME="evony-shield-watch"
PYTHON_BIN="$BOT_DIR/venv/bin/python"

echo "🛡️ Setting up Evony Shield Watch on Oracle VM..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & dependencies
sudo apt install -y python3-pip python3-venv git screen

# Create directory if not exists
mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate and install requirements
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env with your Discord token before starting!"
fi

# Create systemd service
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Evony Shield Watch Discord Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BOT_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$PYTHON_BIN $BOT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit $BOT_DIR/.env with your Discord token"
echo "2. Start bot: sudo systemctl start $SERVICE_NAME"
echo "3. Check status: sudo systemctl status $SERVICE_NAME"
echo "4. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "To run alongside your translate bot, just use a different service name:"
echo "  sudo systemctl start evony-shield-watch"
echo "  sudo systemctl start your-translate-bot"
