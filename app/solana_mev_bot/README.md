# Solana MEV Telegram Bot

This bot monitors Solana transactions for MEV (Miner Extractable Value) activity and sends alerts via Telegram.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/solana_mev_bot.git
   cd solana_mev_bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file and add your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Commands
- `/start`: Start the bot.
- `/help`: Show available commands.
- `/check_mev`: Check for MEV activity.

## Notes
- Ensure you have a stable internet connection.
- Test the bot on Solana testnet before using it on mainnet.