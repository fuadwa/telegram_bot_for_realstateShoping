import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with actual values
admin_chat_id = '7362496291'  # Admin chat ID
BOT_TOKEN = '6910274055:AAFUKcR2gfkegpb9F9XoqX_XT8-ewaGp9RQ'  # Your bot token

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Start command received")
    # Clear previous user data
    context.user_data.clear()
    
    help_text = (
        "Welcome to the Home Selling and Buying Bot!\n\n"
        "Here's how to use the bot:\n"
        "/start - Begin the process to buy or sell a home.\n"
        "1. Choose whether you want to buy or sell a home.\n"
        "2. Enter your name, last name, and phone number.\n"
        "3. Provide a description of the home.\n"
        "4. Send a photo of the home.\n"
        "5. We will send the information to the admin.\n\n"
        "If you need to start over, use /restart."
    )
    await update.message.reply_text(help_text)

    keyboard = [
        [
            InlineKeyboardButton("Buy", callback_data='buy'),
            InlineKeyboardButton("Sell", callback_data='sell'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Do you want to buy or sell a home?', reply_markup=reply_markup)

# Callback query handler for button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['action'] = query.data
    logger.info(f"Button clicked: {query.data}")
    await query.edit_message_text(text=f"Selected option: {query.data}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter your first name:")

# Message handler for collecting user info
async def collect_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    text = update.message.text

    if 'name' not in user_data:
        user_data['name'] = text
        await update.message.reply_text('Please enter your last name:')
    elif 'lastname' not in user_data:
        user_data['lastname'] = text
        await update.message.reply_text('Please enter your phone number:')
    elif 'phone' not in user_data:
        user_data['phone'] = text
        await update.message.reply_text('Please provide a description of the home:')
    elif 'description' not in user_data:
        user_data['description'] = text
        await update.message.reply_text('Please send a photo of the home:')
    elif 'image' not in user_data:
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            user_data['image'] = photo_file.file_id
            await update.message.reply_text('Thank you! Your information has been recorded.')

            # Send collected information to the admin
            if admin_chat_id:
                try:
                    await context.bot.send_message(
                        chat_id=admin_chat_id,
                        text=f"New {user_data.get('action', 'request')} request:\n"
                             f"Name: {user_data['name']}\n"
                             f"Last Name: {user_data['lastname']}\n"
                             f"Phone: {user_data['phone']}\n"
                             f"Description: {user_data['description']}"
                    )
                    # Send the photo
                    if 'image' in user_data:
                        await context.bot.send_photo(chat_id=admin_chat_id, photo=user_data['image'])
                    logger.info("Information successfully sent to admin.")
                except Exception as e:
                    logger.error(f"Failed to send information to admin: {e}")
            else:
                logger.warning("Admin chat ID not set. Unable to send information to admin.")
        else:
            await update.message.reply_text('Please send a photo of the home.')
    else:
        # If the image is already collected, ignore further messages
        await update.message.reply_text('Thank you for your submission!')

# Restart command handler
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Restart command received")
    # Clear previous user data
    context.user_data.clear()
    
    await update.message.reply_text("Welcome back! Please choose whether you want to buy or sell a home:",
                                    reply_markup=InlineKeyboardMarkup([
                                        [InlineKeyboardButton("Buy", callback_data='buy'),
                                         InlineKeyboardButton("Sell", callback_data='sell')]
                                    ]))

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Welcome to the Home Selling and Buying Bot!\n\n"
        "Here's how to use the bot:\n"
        "/start - Begin the process to buy or sell a home.\n"
        "1. Choose whether you want to buy or sell a home.\n"
        "2. Enter your name, last name, and phone number.\n"
        "3. Provide a description of the home.\n"
        "4. Send a photo of the home.\n"
        "5. We will send the information to the admin.\n\n"
        "If you need to start over, use /restart."
    )
    await update.message.reply_text(help_text)

def main() -> None:
    # Create the application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_info))
    application.add_handler(MessageHandler(filters.PHOTO, collect_info))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("restart", restart))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
