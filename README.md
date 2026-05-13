# 🛡️ Evony Shield Watch

Discord bot for **Evony: Return of the King** alliance management.  
Automated bubble reminders, SVS/KE rotation, custom event creation (BOC/BOG/AllStars/Battlefield), and member check-ins.

## Features

| Feature | Description |
|---------|-------------|
| **Auto SVS/KE** | Alternates weekly, starts Friday 5pm your time |
| **1h39m SVS Alert** | First warning before purge attack |
| **1h SVS Alert** | Purge attack + final bubble warning |
| **1h KE Alert** | Single reminder for Kill Event |
| **Local Time PMs** | Each member gets their timezone-converted time |
| **🫧bubble🫧 Channel** | All shield messages go here |
| **Battlefield Channel** | Event rosters, times, player lists |
| **Custom Events** | Coordinators create BOC/BOG/AllStars/BF |
| **Check-in System** | ✅/❌ reactions with cutoff times |
| **Auto Cleanup** | Events delete 10 mins after end |
| **SMS/Pushover** | External notifications (optional) |

## Channel Routing

| Channel Type | What Goes There |
|-------------|-----------------|
| **🫧bubble🫧** | Shield up reminders, purge attack warnings, all bubble-related alerts |
| **battlefield-messages** | Event rosters, player lists, start/end times, BOC/BOG/AllStars/Battlefield announcements |

## Slash Commands

### Setup (Admin)
- `/setup` - Interactive server setup
- `/setbubble [#channel]` - Set/create bubble channel
- `/setbattlefield [#channel]` - Set/create battlefield channel
- `/setcoordinator @role` - Set event coordinator role
- `/addeventcoord @user` - Give coordinator role

### Events (Coordinator)
- `/event_create` - Create custom event (modal popup)
- `/event_cancel <id>` - Cancel event
- `/event_list` - Active events
- `/event_roster <id>` - Show confirmed players

### Admin
- `/forceevent <svs/ke>` - Override current event
- `/contact @user phone <number>` - Set SMS
- `/contact @user pushover <key>` - Set push notifications
- `/broadcast <message>` - DM all members
- `/stats` - Server stats

### Personal
- `/mytime` - Your local reset time
- `/settimezone <timezone>` - Set your timezone
- `/optout` / `/optin` - Control notifications

## Deployment

### Oracle Cloud Free Tier

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/evony-shield-watch.git
cd evony-shield-watch

# Run setup script
chmod +x systemd-service.sh
./systemd-service.sh

# Edit .env
nano .env

# Start bot
sudo systemctl start evony-shield-watch
sudo systemctl enable evony-shield-watch

# View logs
sudo journalctl -u evony-shield-watch -f
