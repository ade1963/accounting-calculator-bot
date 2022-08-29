#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position, invalid-escape-sequence

"""
AccountingCalculatorBot demonstrates how telegram can be enriched with external web app.

User can launch Web App with Keyboard Button, make some calculations and receive history back in bots chat.
There exists 4 different ways user can launch Web App but only Keyboard Button supports receiving data back.
"""

import logging
import re
from logging import handlers

from dotenv import load_dotenv
from telegram import Update, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from os import environ

# get parameters from environment or local .env file
load_dotenv('.env')
CALC_URL = 'https://accountingcalculator-37edb.web.app'
BOT_TOKEN = environ['ACCOUNTING_CALCULATOR_BOT_TOKEN']
ADMIN_CHANT_ID = environ['ADMIN_CHANT_ID']
LOG_NAME = environ['LOG_NAME']

logger = logging.getLogger(__name__)


def get_math_result(calc_history):
    """ Get the last number from history """
    match = re.search(r'([\d\.]+)$', calc_history)
    if match:
        return match.group(1)
    else:
        return ''


def make_calc_keyboard(init_value=''):
    """ Show Keyboard Button to launch Web App"""
    but_caption = "Call calculator"
    url = CALC_URL
    # add number from previous calculations
    if init_value:
        url += f'?value={init_value}'
        but_caption += f' with last value={init_value}'

    web_info = WebAppInfo(url=url)
    button = [[KeyboardButton(but_caption, web_app=web_info)]]
    return ReplyKeyboardMarkup(button, one_time_keyboard=True, resize_keyboard=True)


def set_logger():
    """ Save logs to file"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    hdlr = handlers.WatchedFileHandler(LOG_NAME)
    hdlr.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(hdlr)


def start_cmd(update: Update, context: CallbackContext) -> None:
    """ Called when new user is subscribed"""
    user = update.effective_user
    update.message.reply_markdown_v2(
        f'Hi {user.mention_markdown_v2()}\!\n\n'
        f'This bot uses Accounting Calculator to store history of your calculations\n\n'
        f'Source code is available\.\n'
        f'Bot \(Python\): https://github\.com/ade1963/accounting\-calculator\-bot\.git\n'
        f'Calculator \(Flutter\): https://github\.com/ade1963/flutter\-accounting\-calculator\.git\n\n'
        f'Commands:\n'
        f'/help\n'
        f'/calc \- show Keyboard Button to call "web app" Calculator\.\n'
        f'/feedback \.\.\.some text\.\.\. \- send message to admin\. Type text in same line with the command\.\n',
        reply_markup=make_calc_keyboard(),
    )
    logger.info(f'Start - {user.mention_markdown_v2()}')


def help_cmd(update: Update, context: CallbackContext) -> None:
    """ Command /help """
    user = update.effective_user
    update.message.reply_markdown_v2(
        'Bot can be used to store history of private calculations\.\n\n'
        f'/help\n'
        f'/calc \- show Keyboard Button to call "web app" Calculator\.\n'
        f'/feedback \.\.\.some text\.\.\. \- send message to admin\. Type text in same line with the command\.\n',
        reply_markup=make_calc_keyboard())
    logger.info(f'Help - {user.mention_markdown_v2()}')


def feedback_cmd(update: Update, context: CallbackContext) -> None:
    """Command /feedback - send message to bots admin"""
    user = update.effective_user
    update.message.reply_text(
        f'{user.mention_markdown_v2()}, thank you\n',
        reply_markup=make_calc_keyboard())

    message = f'Feedback from {user.mention_markdown_v2()}, chat_id:{user.id}:\n{update.effective_message.text}'
    context.bot.send_message(chat_id=ADMIN_CHANT_ID, text=message)


def calc_button_cmd(update: Update, context: CallbackContext) -> None:
    """ Command /calc - create Keyboard Button"""
    user = update.effective_user
    logger.info(f'Calc_button - {user.mention_markdown_v2()}')
    message = "Press the button to call Web-Calculator"
    update.effective_message.reply_text(
        message, reply_markup=make_calc_keyboard()
    )


def web_app_data(update: Update, context: CallbackContext) -> None:
    """ Receive data from Calculator Web App"""
    user = update.effective_user
    logger.info(f'Web_app_data - {user.mention_markdown_v2()}')
    calc_history = update.message.web_app_data.data
    calc_history = '\n'.join(calc_history.split('\n')[::-1])
    last_value = get_math_result(calc_history)

    update.effective_message.reply_text(calc_history, reply_markup=make_calc_keyboard(last_value))


def connected_website(update: Update, context: CallbackContext) -> None:
    """ Log event when user launch Web App"""
    user = update.effective_user
    logger.info(f'Connected_website - {user.mention_markdown_v2()}')


def main() -> None:
    """ Enable logging and start polling for user activity"""
    set_logger()
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_cmd))
    dispatcher.add_handler(CommandHandler("help", help_cmd))
    dispatcher.add_handler(CommandHandler("calc", calc_button_cmd))
    dispatcher.add_handler(CommandHandler("feedback", feedback_cmd))

    dispatcher.add_handler(MessageHandler(Filters.status_update.web_app_data, web_app_data))
    dispatcher.add_handler(MessageHandler(Filters.status_update.connected_website, connected_website))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
