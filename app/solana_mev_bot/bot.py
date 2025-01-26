import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from solana.rpc.api import Client
from solana.rpc.websocket_api import connect
from solana.publickey import PublicKey
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables (e.g., Telegram bot token)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
SOLANA_WS_URL = "wss://api.mainnet-beta.solana.com"
TOKEN_CONTRACT_ADDRESS = "7TTcLchHbXz5fQqbBcoWi1Zen87AiziaqFCrf9Enpump"

# Initialize Solana client
solana_client = Client(SOLANA_RPC_URL)

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define command handlers
async def start(update: Update, context):
    await update.message.reply_text("Welcome! Use /help to see available commands.")

async def help_command(update: Update, context):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/check_mev - Check for MEV activity"
    )

async def check_mev(update: Update, context):
    await update.message.reply_text("Checking for MEV activity...")
    try:
        transactions = await fetch_token_transactions()
        mev_transactions = detect_mev(transactions)
        if mev_transactions:
            message = format_mev_message(mev_transactions)
            await send_mev_alert(update, context, message)
        else:
            await update.message.reply_text("No MEV activity detected.")
    except Exception as e:
        logger.error(f"Error in check_mev: {e}", exc_info=True)
        await update.message.reply_text("An error occurred while checking for MEV activity.")

# Error handler
async def error_handler(update: Update, context):
    logger.error(f"Update {update} caused error {context.error}", exc_info=True)
    await update.message.reply_text("An error occurred. Please try again.")

# Fetch transactions involving the token contract
async def fetch_token_transactions():
    try:
        token_pubkey = PublicKey(TOKEN_CONTRACT_ADDRESS)
        transactions = solana_client.get_signatures_for_address(token_pubkey)
        if transactions and 'result' in transactions:
            return transactions['result']
        return []
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}", exc_info=True)
        return []

# Parse transaction details
def parse_transaction(transaction):
    try:
        tx_id = transaction.get("signature", "Unknown")
        timestamp = transaction.get("blockTime", "Unknown")
        wallet_address = transaction.get("owner", "Unknown")
        amount = transaction.get("amount", 0)  # Placeholder for actual amount parsing
        return tx_id, timestamp, wallet_address, amount
    except Exception as e:
        logger.error(f"Error parsing transaction: {e}", exc_info=True)
        return "Unknown", "Unknown", "Unknown", 0

# Define MEV detection heuristics
def detect_mev(transactions):
    mev_transactions = []
    for tx in transactions:
        # Example heuristic: High gas fees or rapid succession of transactions
        if tx.get("fee", 0) > 1000000:  # Placeholder for actual fee threshold
            mev_transactions.append(tx)
    return mev_transactions

# Format MEV activity message
def format_mev_message(mev_transactions):
    message = "🚨 MEV Activity Detected 🚨\n\n"
    for tx in mev_transactions:
        tx_id, timestamp, wallet_address, amount = parse_transaction(tx)
        message += (
            f"Transaction ID: {tx_id}\n"
            f"Wallet: {wallet_address}\n"
            f"Amount: {amount} SOL\n"
            f"Timestamp: {timestamp}\n\n"
        )
    return message

# Send MEV activity message to Telegram
async def send_mev_alert(update: Update, context, message):
    await update.message.reply_text(message)

# Monitor Solana blockchain for new transactions
async def monitor_transactions(update: Update, context):
    try:
        async with connect(SOLANA_WS_URL) as websocket:
            await websocket.logs_subscribe()
            while True:
                message = await websocket.recv()
                if message:
                    transactions = await fetch_token_transactions()
                    mev_transactions = detect_mev(transactions)
                    if mev_transactions:
                        message = format_mev_message(mev_transactions)
                        await send_mev_alert(update, context, message)
                await asyncio.sleep(1)  # Polling interval
    except Exception as e:
        logger.error(f"Error in monitor_transactions: {e}", exc_info=True)
        await update.message.reply_text("An error occurred while monitoring transactions.")

# Set up the bot
def setup_bot():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check_mev", check_mev))

    # Add error handler
    application.add_error_handler(error_handler)

    return application

# Main function to run the bot
async def main():
    try:
        application = setup_bot()
        await application.run_polling()
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())