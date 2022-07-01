# Leech Settings V2 Implement By - @VarnaX-279

from os import remove as osremove, path as ospath, mkdir
import os
from threading import Thread
from PIL import Image
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup

from bot import AS_DOC_USERS, AS_MEDIA_USERS, dispatcher, AS_DOCUMENT, app, AUTO_DELETE_MESSAGE_DURATION, DB_URI
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, auto_delete_message, sendPhoto
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper import button_build
from bot.helper.ext_utils.db_handler import DbManger


def getleechinfo(from_user):
    user_id = from_user.id
    name = from_user.full_name
    buttons = button_build.ButtonMaker()
    thumbpath = os.path.join("Thumbnails", f"{user_id}.jpg")
    if (
        user_id in AS_DOC_USERS
        or user_id not in AS_MEDIA_USERS
        and AS_DOCUMENT
    ):
        ltype = "DOCUMENT"
        buttons.sbutton("Send As Media", f"leechset {user_id} med")
    else:
        ltype = "MEDIA"
        buttons.sbutton("Send As Document", f"leechset {user_id} doc")

    if ospath.exists(thumbpath):
        thumbmsg = "Exists"
        buttons.sbutton("Delete Thumbnail", f"leechset {user_id} thumb")
        buttons.sbutton("Show Thumbnail", f"leechset {user_id} showthumb")
    else:
        thumbmsg = "Not Exists"

    if AUTO_DELETE_MESSAGE_DURATION == -1:
        buttons.sbutton("Close", f"leechset {user_id} close")

    button = InlineKeyboardMarkup(buttons.build_menu(1))

    text = f"Leech Settings\nUser: <a href='tg://user?id={user_id}'>{name}</a> (<code>{str(user_id)}</code>)\n"\
           f"Leech Type: {ltype}\n"\
           f"Custom Thumbnail: {thumbmsg}"
    return text, button

def editLeechType(message, query):
    msg, button = getleechinfo(query.from_user)
    editMessage(msg, message, button)

def leechSet(update, context):
    msg, button = getleechinfo(update.message.from_user)
    choose_msg = sendMarkup(msg, context.bot, update, button)
    Thread(target=auto_delete_message, args=(context.bot, update.message, choose_msg)).start()

def setLeechType(update, context):
    query = update.callback_query
    message = query.message
    user_id = query.from_user.id
    data = query.data
    data = data.split(" ")
    path = str(os.path.join("Thumbnails", f"{user_id}.jpg"))
    if user_id != int(data[1]): query.answer(text="Not Yours.")
    elif data[2] == "doc":
        if user_id in AS_MEDIA_USERS: AS_MEDIA_USERS.remove(user_id)
        AS_DOC_USERS.add(user_id)
        if DB_URI: DbManger().user_doc(user_id)
        query.answer(text="Your File Will Deliver As Document.")
        editLeechType(message, query)
    elif data[2] == "med":
        if user_id in AS_DOC_USERS: AS_DOC_USERS.remove(user_id)
        AS_MEDIA_USERS.add(user_id)
        if DB_URI: DbManger().user_media(user_id)
        query.answer(text="Your File Will Deliver As Media.")
        editLeechType(message, query)
    elif data[2] == "thumb":
        if ospath.lexists(path):
            osremove(path)
            if DB_URI: DbManger().user_rm_thumb(user_id, path)
            query.answer(text="Thumbnail removed.")
            editLeechType(message, query)
        else: query.answer(text="Send new settings command.")
    elif data[2] == "showthumb":
        if ospath.lexists(path):
            msg = f"Thumbnail for: <a href='tg://user?id={user_id}'>{query.from_user.full_name}</a> (<code>{str(user_id)}</code>)"
            delo = sendPhoto(text=msg, bot=context.bot, message=message, photo=open(path, 'rb'))
            Thread(target=auto_delete_message, args=(context.bot, update.message, delo)).start()
        else: query.answer(text="Send new settings command.")
    elif data[2] == "close":
        try:
            query.message.delete()
            query.message.reply_to_message.delete()
        except:
            pass

def setThumb(update, context):
    user_id = update.message.from_user.id
    reply_to = update.message.reply_to_message
    if reply_to is not None and reply_to.photo:
        path = "Thumbnails/"
        if not ospath.isdir(path):
            mkdir(path)
        photo_msg = app.get_messages(update.message.chat.id, reply_to_message_ids=update.message.message_id)
        photo_dir = app.download_media(photo_msg, file_name=path)
        des_dir = ospath.join(path, f"{str(user_id)}.jpg")
        Image.open(photo_dir).convert("RGB").save(des_dir, "JPEG")
        osremove(photo_dir)
        if DB_URI is not None:
            DbManger().user_save_thumb(user_id, des_dir)
        msg = f"Custom thumbnail saved for: <a href='tg://user?id={user_id}'>{update.message.from_user.full_name}</a> (<code>{str(user_id)}</code>)"
        todel = sendMessage(msg, context.bot, update)
    else:
        todel = sendMessage("Reply to a photo to save custom thumbnail.", context.bot, update)

    Thread(target=auto_delete_message, args=(context.bot, update.message, todel)).start()

leech_set_handler = CommandHandler(BotCommands.LeechSetCommand, leechSet, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
set_thumbnail_handler = CommandHandler(BotCommands.SetThumbCommand, setThumb, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
but_set_handler = CallbackQueryHandler(setLeechType, pattern="leechset", run_async=True)

dispatcher.add_handler(leech_set_handler)
dispatcher.add_handler(but_set_handler)
dispatcher.add_handler(set_thumbnail_handler)

