from telegram import (CallbackQuery, InlineKeyboardButton,
                      InlineKeyboardMarkup, ParseMode, Update)
from telegram.ext import CallbackContext

from ..db import db
from ..models import Expense
from ..utils import parse_user_alias
from .balances import compute_balances, format_balances, is_even_stephanie


def clear(update: Update, context: CallbackContext):
  keyboard = [
    [InlineKeyboardButton('Yes', callback_data='clear_yes')],
    [InlineKeyboardButton('Cancel', callback_data='clear_no')],
  ]

  update.message.reply_text(
    '🫢 Are you sure you want to clear all expenses?',
    reply_markup=InlineKeyboardMarkup(keyboard),
    quote=False,
  )

def clear_query_yes(query: CallbackQuery, context: CallbackContext):
  chat_id = query.message.chat.id
  expenses = Expense.query.filter_by(chat_id=chat_id)
  user_alias = parse_user_alias(query.from_user)

  if expenses.count() < 1:
    query.edit_message_text(
      'Nothing to clear 🫠',
      parse_mode=ParseMode.MARKDOWN,
    )
  else:
    try:
      balances_by_user = compute_balances(chat_id)
      expenses.delete()
      db.session.commit()
    except Exception as exc:
      db.session.rollback()
      raise exc

    reply = f'🙂 All expenses are cleared by {user_alias}, here\'re the last outstanding balances 👇'
    reply += '\n\n'

    if is_even_stephanie(balances_by_user):
      reply += 'No one owes anyone anything, even-stephanie 🥳'
    else:
      reply += format_balances(balances_by_user)

    query.edit_message_text(
      reply,
      parse_mode=ParseMode.MARKDOWN,
    )

def clear_query_no(query: CallbackQuery, context: CallbackContext):
  user_alias = parse_user_alias(query.from_user)
  query.edit_message_text(text=f'🙂 Clear command cancelled by {user_alias}')
