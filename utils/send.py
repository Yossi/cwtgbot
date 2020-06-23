import logging
import filetype


def send(payload, update, context):
    chat_id = update.effective_message.chat_id
    if isinstance(payload, str):
        max_size = 4096
        for text in [payload[i:i + max_size] for i in range(0, len(payload), max_size)]:
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