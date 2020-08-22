import logging
import re

import filetype
from telegram import ParseMode


def send(payload, update, context):
    n = 100 # number of formatted entities tg allows per message
    chat_id = update.effective_message.chat_id
    if isinstance(payload, str):
        max_size = 4096
        i = 0
        while i < len(payload):
            text = payload[i:i + max_size]
            open_tags = text.count('<')
            consumed_chars = max_size
            if open_tags != text.count('>'): # cut mid tag
                consumed_chars = text.rfind('<')
                text = text[:consumed_chars]
                open_tags -= 1
            if open_tags % 2: # close tag missing
                consumed_chars = text.rfind('<')
                text = text[:consumed_chars]
                open_tags -= 1
            if open_tags > 2 * n: # too many tag pairs
                consumed_chars = [m.start() for m in re.finditer(r'<', text)][2 * n]
                text = text[:consumed_chars]
            i = i + consumed_chars

            logging.info(f'bot said:\n{text}')
            context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        kind = filetype.guess(payload.read(261))
        payload.seek(0)
        if kind and kind.mime.startswith('image'):
            logging.info(f'bot said:\n<image>')
            context.bot.send_photo(chat_id=chat_id, photo=payload)
        else:
            logging.info(f'bot said:\n<other>')
            context.bot.send_document(chat_id=chat_id, document=payload)
