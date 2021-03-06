import json
import requests
import re
from flask import Flask, request
import telegram
from telebot.credentials import bot_token, bot_user_name, URL

global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    # for debugging purposes only
    print("got text message :", text)
    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
       Приветствие, напишите сообщение для instagram.
       """
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

    else:
        try:
            # clear the message we got from any non alphabets
            text = re.sub(r"\W", "_", text)

            url = "https://zeapi.yandex.net/lab/api/yalm/text3"
            payload = json.dumps({"query": text, "intro": 7, "filter": 1})
            headers = {
                "Content-Type": "application/json",
                "Referrer-Policy": "unsafe-url",
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print("RESPONSE", response.text)
            caption = response["query"] + response["text"]

            bot.sendMessage(chat_id=chat_id, text=caption, reply_to_message_id=msg_id)
        except Exception:
            # if things went wrong
            bot.sendMessage(chat_id=chat_id,
                            text="There was a problem in the name you used, please enter different name",
                            reply_to_message_id=msg_id)

    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return '.'


if __name__ == '__main__':
    app.run(threaded=True)
