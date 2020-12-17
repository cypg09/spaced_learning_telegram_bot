import requests
import traceback
import time
from threading import Thread, Lock


class TelegramReceiver(Thread):
    def __init__(self,
                 telegram_logger,
                 bot_token):
        Thread.__init__(self)
        self.tl = telegram_logger
        self.tl.info("TelegramReceiver: begin init.")
        self.lock = Lock()
        self.bot_token = bot_token
        self.messages = {}
        self.last_date = 0
        self.tl.info("TelegramReceiver: init done.")

    def get_messages(self):
        while True:
            try:
                url = 'https://api.telegram.org/bot' + self.bot_token + '/getUpdates?limit=100'
                _answer = requests.get(url)
                _answer = _answer.json()['result']
            except:
                time.sleep(0.5)
                continue
            if len(_answer) == 0:
                time.sleep(0.05)
                continue
            else:
                return _answer

    def handle_messages(self, _answer, messages):
        try:
            this_date = 0
            for element in _answer:
                if 'message' in element:
                    message_content = element['message']
                    this_text = message_content['text']
                else:
                    continue
                this_chat_id = str(message_content['chat']['id'])
                this_date = float(message_content['date'])
                if float(this_date) > self.last_date:
                    if isinstance(messages, dict) and this_chat_id in list(messages.keys()):
                        messages[this_chat_id].append(this_text)
                    elif isinstance(messages, dict):
                        messages[this_chat_id] = [this_text]
                    else:
                        messages = {this_chat_id: [this_text]}
                    self.last_date = float(this_date)
            try:
                self.tl.debug(messages)
                # Send offset
                requests.get(
                    'https://api.telegram.org/bot' + self.bot_token + '/getUpdates?limit=100'
                                                                      '&offset=' + str(this_date)
                )
            except:
                pass
            return messages
        except:
            self.tl.error(traceback.format_exc())

    def run(self):
        while True:
            __answer = self.get_messages()
            self.messages = self.handle_messages(__answer, self.messages)
            time.sleep(0.05)
