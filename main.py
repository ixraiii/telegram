from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup
import aiohttp
import logging
import re  # For keyword detection

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to check if the anime is available by scraping the site
async def is_anime_available(anime_name):
    search_url = f"https://www.blakiteanime.fun/search?q={anime_name.replace(' ', '+')}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                if response.status == 200:
                    page_content = await response.text()
                    soup = BeautifulSoup(page_content, 'html.parser')
                    results = soup.find_all('div', class_='hentry play c:hover-eee')
                    if results:
                        return True, search_url
                    else:
                        return False, search_url
                else:
                    return False, search_url
    except aiohttp.ClientError:
        logger.error("Failed to fetch anime details.", exc_info=True)
        return False, search_url

# Command to display help message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I can help you search for anime links.\n\n"
        "To search, mention me or use keywords like `bot` followed by the anime name.\n"
        "Example: `Naruto bot`, `@YourBotUsername Naruto`\n\n"
        "For any issues, visit the support group: t.me/blakitechats."
    )

# Function to handle user messages and respond
async def search_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    bot_username = (await context.bot.get_me()).username  # Get the bot's username dynamically

    # Check if the message contains a bot mention, @botusername, or "bot" keyword
    if f"@{bot_username}" in message.text or re.search(r'\b(bot|@bot)\b', message.text, re.IGNORECASE):
        # Extract the anime name by removing the bot mention or keyword
        anime_name = re.sub(rf'@{bot_username}|bot|@bot', '', message.text, flags=re.IGNORECASE).strip()
        if anime_name:
            await message.reply_text("Please wait... Searching now...")
            available, search_url = await is_anime_available(anime_name)
            if available:
                reply_message = (
                    f"Here is your link: [{anime_name}]({search_url})\n"
                    f"Let me know if you want more.\n"
                    f"Stay tuned!"
                )
                await message.reply_text(reply_message, parse_mode='Markdown')
            else:
                reply_message = (
                    "Sorry, we couldn't find that anime.\n"
                    "Please check the name or try again.\n"
                    "If the anime is not available, go to the support group: t.me/blakitechats and comment there."
                )
                await message.reply_text(reply_message)
        else:
            await message.reply_text("Please mention an anime name after calling me!")
    else:
        # Ignore messages that do not mention the bot or contain the keyword
        return

# Main function to set up the bot
def main():
    application = Application.builder().token("7803638695:AAGY4G0A8qCImLZkGZnGGFBRzOwG9AqeAkc").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))

    # Add a message handler for user text input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_anime))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
