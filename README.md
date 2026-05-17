# 🛡️ Evony Shield Watch

Discord bot for **Evony: Return of the King** alliance management.

Automates:
- SVS / KE event rotation
- Shield warnings and purge alerts
- Custom alliance events (BOC / BOG / AllStars / Battlefield)
- Member onboarding + opt-in tracking
- Discord + Telegram notification system

---

## 🚀 Features

| Feature | Description |
|--------|-------------|
| 🔄 SVS / KE Engine | Automatic weekly rotation system |
| ⚠️ SVS Alerts | 1h39m purge + 1h warning system |
| ⚔️ KE Alerts | Combat activation + shield reminders |
| 🌍 Timezone System | Member-local reset time conversion |
| 📲 Telegram Linking | Optional Telegram alert bridge |
| 🛡️ Opt-In System | Members control notifications |
| 🧭 Role System | Member / Coordinator / Admin / Owner |
| 📋 Custom Events | Create BOC / BOG / AllStars / Battlefield |
| ✅ Check-in System | Reaction-based participation tracking |
| 🧹 Auto Cleanup | Events expire after completion |

---

## 📡 Notification System

### Discord Alerts
- SVS / KE war alerts
- Custom event announcements
- Admin broadcasts
- Event rosters & check-ins

### Telegram Alerts (Optional)
- Linked via `/linktelegram`
- Token-based secure pairing
- Opt-in required per user
- Safe fallback (system still works without it)

---

## 🧠 Smart Safety Logic

### SVS (Server War)
- ❌ Relics are NOT safe  
- ❌ Tiles are NOT safe  
- ❌ Arctic Barbarians are NOT safe  
- ❌ Pyramid events are NOT safe  
- ⚠️ Assume all PvE zones are dangerous  

### KE (Kill Event)
- 🛡️ Bubble up if not fighting  
- ✅ Relics are safe  
- ✅ Tiles are safe  
- ✅ Barbarians are safe  
- ✅ Pyramid events are safe  

---

## 🧾 Slash Commands

### ⚙️ Setup (Admin)
- `/setup` – Server configuration wizard
- `/setbubble #channel`
- `/setbattlefield #channel`
- `/setcoordinator @role`

---

### ⚔️ Events (Coordinator)
- `/event_create`
- `/event_cancel <id>`
- `/event_list`
- `/event_roster <id>`

---

### 🛡️ Admin
- `/forceevent svs|ke`
- `/broadcast <message>`
- `/stats`

---

### 👤 Personal
- `/mytime`
- `/settimezone <timezone>`
- `/optin`
- `/optout`
- `/linktelegram`
- `/unlinktelegram`

---

## 🏗️ Architecture
