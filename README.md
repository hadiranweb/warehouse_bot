# Warehouse Bot
A simple Telegram bot for warehouse management, built with Python.

## Features
- Add new items: `/add <name> <quantity>`
- List inventory: `/list`
- Delete items: `/delete <id>`
- Start: `/start`

## Setup
1. **Install Python 3.8+** if not already installed.
2. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd warehouse_bot
Install dependencies:
bash

pip install -r requirements.txt

Get a Telegram Bot Token:
Message @BotFather
 on Telegram.

Use /newbot to create a bot and get the token.

Create .env file:
bash

echo "TELEGRAM_TOKEN=your_bot_token_here" > .env

Run the bot:
bash

python bot.py

Usage
/start: Welcome message.

/add Apple 10: Add 10 apples to inventory.

/list: Show all items.

/delete 1: Delete item with ID 1.

