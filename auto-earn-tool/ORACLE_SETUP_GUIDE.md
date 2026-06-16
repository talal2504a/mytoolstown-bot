# Oracle Cloud Free Tier - Step by Step Setup Guide
## 24/7 Bot Deployment (Completely Free)

---

## Step 1: Sign Up for Oracle Cloud
1. Go to: **https://www.oracle.com/cloud/free/**
2. Click **"Start for free"**
3. Fill in your details:
   - Email, password, country
   - Phone number for verification
   - Credit card (for identity verification only - **will NOT be charged** if you stay in free tier)
4. Verify your email and phone
5. Sign in to Oracle Cloud console

---

## Step 2: Create a Free VM (Compute Instance)

1. In Oracle Cloud Console, click **"Create a VM instance"**
2. Give it a name: `mytoolstown-bot`
3. **Image**: Select **"Canonical Ubuntu 22.04"** (or 24.04)
4. **Shape**: Select **"VM.Standard.E2.1.Micro"** (always free - 1GB RAM)
   - *Note: Sometimes this is unavailable, try "VM.Standard.A1.Flex" with 1 OCPU + 6GB RAM - also free*
5. **SSH Keys**: 
   - Select **"Generate SSH key pair"**
   - Click **"Save Private Key"** → download to your PC
   - Click **"Save Public Key"** → download
6. **Boot volume**: 50GB (free)
7. Click **"Create"**

---

## Step 3: Get Your Server IP
- After creation, wait 1-2 minutes
- Note down the **Public IP Address** (e.g., `129.xxx.xxx.xxx`)

---

## Step 4: Upload Bot Files to Server

### Windows Users - Using WinSCP (Easy):
1. Download WinSCP: https://winscp.net/
2. Open WinSCP → File Protocol: **SFTP**
3. Host name: **Your Server IP**
4. Port: **22**
5. Username: **ubuntu** (or **opc** for Oracle Linux)
6. SSH Key: Select the private key you downloaded
7. Click **Login**
8. Drag & drop the `auto-earn-tool` folder to the server

### Windows Users - Using CMD (Alternative):
```cmd
scp -i C:\path\to\ssh-key.ppk -r "e:\insta tool 2\auto-earn-tool" ubuntu@YOUR_SERVER_IP:~/bot
```

---

## Step 5: SSH Into Server & Run Setup

### Windows - Using PuTTY:
1. Download PuTTY: https://www.putty.org/
2. Host: **Your Server IP**, Port: **22**
3. Connection → SSH → Auth → Credentials: Browse to your private key
4. Username: **ubuntu**
5. Click **Open**
6. Paste these commands:

```bash
# Go to bot folder
cd ~/bot

# Make setup script executable
chmod +x setup_free_server.sh

# Fix the setup script - remove the Python docstring at top
sed -i '1,12d' setup_free_server.sh

# Run setup (this takes 2-3 minutes)
bash setup_free_server.sh
```

---

## Step 6: Configure Your Username

```bash
# Edit config.json
nano config.json
```

Change `"YOUR_USERNAME_HERE"` to your actual Instagram username:
```json
"instagram_username": "your_actual_username"
```

Save: `Ctrl+X` → `Y` → `Enter`

---

## Step 7: Test the Bot

```bash
# Run once to test
python3 server_bot.py
```

Wait 30 seconds to see it working. Then press `Ctrl+C` to stop.

---

## Step 8: Run 24/7 (Even After You Close Terminal)

### Method A: Using screen (Simple)
```bash
# Install screen
sudo apt install -y screen

# Create a screen session
screen -S bot

# Start the bot
cd ~/bot
python3 server_bot.py
```

Now press `Ctrl+A` then `D` to detach.
Bot runs 24/7! To check later:
```bash
screen -r bot
```

### Method B: Using systemd (Auto-start on reboot) ⭐ RECOMMENDED

```bash
# Copy service file
sudo cp mytoolstown-bot.service /etc/systemd/system/

# Edit service file to fix paths
sudo nano /etc/systemd/system/mytoolstown-bot.service
```

Change `/root/bot` to `/home/ubuntu/bot`:
```
WorkingDirectory=/home/ubuntu/bot
ExecStart=/usr/bin/python3 /home/ubuntu/bot/server_bot.py
```

Save: `Ctrl+X` → `Y` → `Enter`

```bash
# Enable auto-start
sudo systemctl daemon-reload
sudo systemctl enable mytoolstown-bot
sudo systemctl start mytoolstown-bot

# Check status
sudo systemctl status mytoolstown-bot

# View logs
tail -f ~/bot/server_bot.log
```

---

## 📊 Monitoring Your Bot

```bash
# View live logs
tail -f ~/bot/server_bot.log

# Check if bot is running
ps aux | grep python3

# Restart bot
sudo systemctl restart mytoolstown-bot

# Stop bot
sudo systemctl stop mytoolstown-bot
```

---

## ⚠️ Important Notes

1. **Oracle Free Tier Limits**: You get 2 VMs + 200GB storage free forever
2. **Credit Card**: Oracle charges $0 for free tier, but needs card for verification
3. **If shape is unavailable**: Try different regions (US East, UK South, etc.)
4. **Bot uses ~500MB RAM** - fits in Oracle's free 1GB instance
5. **To check logs remotely**: Just SSH and run `tail -f ~/bot/server_bot.log`

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't SSH (timeout) | Go to Oracle Cloud → Instance → Security Lists → Add ingress rule for port 22 |
| Playwright fails | Run: `python3 -m playwright install chromium --force` |
| Bot crashes | Check logs: `tail -50 ~/bot/server_bot.log` |
| Session expired | Bot auto-restarts, but if stuck: `sudo systemctl restart mytoolstown-bot` |

---

**Done!** Aapka bot ab **24/7 Oracle Cloud free server** par chal raha hai! 🚀