from threading import Thread
import traceback
import spaced_learning as sl
import telegram as tg
from time import sleep


class MainClass(Thread):
    """
    Main class which launches subclasses and runs the script.
    """

    def __init__(self,
                 telegram_logger, bot_token
                 ):
        Thread.__init__(self)
        self.tl = telegram_logger
        self.tl.info("MainClass: begin init.")
        self.bot_token = bot_token
        self.sl_bots = []
        self.sl_chat_ids = []
        self.tl.info("MainClass: init tg_receiver.")
        self.tg_receiver = tg.TelegramReceiver(self.tl, self.bot_token)
        self.tg_receiver.start()
        self.tl.info("MainClass: init done.")

    def get_messages(self):
        self.tg_receiver.lock.acquire()
        messages = self.tg_receiver.messages
        self.tg_receiver.messages = {}
        self.tg_receiver.lock.release()
        return messages

    def telegram_handler(self):
        messages = self.get_messages()
        for chat_id in messages.keys():
            if chat_id not in self.sl_chat_ids:
                new_sl_bot = sl.OwnSpacedLearnHub(self.tl,
                                                  self.bot_token,
                                                  chat_id
                                                  )
                self.sl_bots.append(new_sl_bot)
                self.sl_chat_ids.append(chat_id)
                self.tl.info(f"New client : {chat_id}")
                new_sl_bot.tutorial()
        for bot in self.sl_bots:
            try:
                bot.from_messages_dict_to_list(messages)
            except:
                self.tl.error(traceback.format_exc())
        return

    def run(self) -> None:
        while True:
            for bot in self.sl_bots:
                bot.run()
            self.telegram_handler()
            sleep(1)
