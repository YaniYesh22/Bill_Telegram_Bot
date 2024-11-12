from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os

# States for conversation
BILL = 0
TIP = 1
PEOPLE = 2

# Common tip percentages
TIP_OPTIONS = [['10%', '12%', '15%'], ['18%', '20%', 'Custom']]

# Common people counts
PEOPLE_OPTIONS = [['1', '2', '3'], ['4', '5', '6'], ['Custom']]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation and ask for the bill amount."""
    await update.message.reply_text(
        "Welcome to Bill Splitter Bot! 🧾\n"
        "Let's split your bill.\n"
        "First, please enter the total bill amount:"
    )
    return BILL

async def bill_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the bill amount and ask for tip percentage with keyboard."""
    try:
        bill = float(update.message.text)
        if bill <= 0:
            await update.message.reply_text("Please enter a valid positive amount:")
            return BILL
        
        context.user_data['bill'] = bill
        
        # Create custom keyboard for tips
        reply_markup = ReplyKeyboardMarkup(
            TIP_OPTIONS,
            one_time_keyboard=True,
            resize_keyboard=True
        )
        
        await update.message.reply_text(
            "Great! Select a tip percentage or choose 'Custom' to enter your own:",
            reply_markup=reply_markup
        )
        return TIP
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return BILL

async def tip_percentage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the tip percentage and ask for number of people."""
    text = update.message.text.replace('%', '')
    
    if text == 'Custom':
        await update.message.reply_text(
            "Enter your custom tip percentage (just the number, e.g. 15):",
            reply_markup=ReplyKeyboardRemove()
        )
        return TIP
    
    try:
        tip = float(text)
        if tip < 0:
            await update.message.reply_text("Please enter a valid tip percentage:")
            return TIP
        
        context.user_data['tip'] = tip
        
        # Create custom keyboard for people count
        reply_markup = ReplyKeyboardMarkup(
            PEOPLE_OPTIONS,
            one_time_keyboard=True,
            resize_keyboard=True
        )
        
        await update.message.reply_text(
            "Perfect! Select the number of people splitting the bill:",
            reply_markup=reply_markup
        )
        return PEOPLE
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number or select from the options:",
            reply_markup=ReplyKeyboardMarkup(
                TIP_OPTIONS,
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return TIP

async def people_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculate and show the final split amount."""
    text = update.message.text
    
    if text == 'Custom':
        await update.message.reply_text(
            "Enter the number of people:",
            reply_markup=ReplyKeyboardRemove()
        )
        return PEOPLE
    
    try:
        people = int(text)
        if people <= 0:
            await update.message.reply_text(
                "Please enter a valid number of people:",
                reply_markup=ReplyKeyboardMarkup(
                    PEOPLE_OPTIONS,
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            return PEOPLE
        
        bill = context.user_data['bill']
        tip = context.user_data['tip']
        
        tip_amount = bill * (tip / 100)
        total = bill + tip_amount
        per_person = total / people
        
        await update.message.reply_text(
            f"💰 Bill Summary 💰\n"
            f"Bill amount: ₪{bill:.2f}\n"
            f"Tip ({tip}%): ₪{tip_amount:.2f}\n"
            f"Total amount: ₪{total:.2f}\n"
            f"Each person pays: ₪{per_person:.2f}\n\n"
            f"To split another bill, use /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number or select from the options:",
            reply_markup=ReplyKeyboardMarkup(
                PEOPLE_OPTIONS,
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return PEOPLE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text(
        "Operation cancelled. Use /start to split a new bill.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    """Start the bot."""
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
    application = Application.builder().token('Change to your telegram bot token').build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BILL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bill_amount)],
            TIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, tip_percentage)],
            PEOPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, people_count)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
