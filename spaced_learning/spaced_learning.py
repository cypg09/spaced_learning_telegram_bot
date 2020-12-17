import pandas as pd
import requests
import traceback
from random import randint
import datetime


def get_today():
    today = int(str(datetime.date.today())[-2:])
    return today


def get_hour():
    return datetime.datetime.now().hour


class OwnSpacedLearnHub:
    """
    One per user ; contains an array with the description of the J, the date of each J,
    and a self.check (bool) : True if J has been learnt.
    """

    def __init__(self,
                 telegram_logger, telegram_bot_token,
                 chat_id):
        self.tl = telegram_logger
        self.tl.info("New OwnSpacedLearnHub: begin init.")
        self.bot_token = telegram_bot_token
        self.chat_id = chat_id
        self.days = [7, 16, 35]
        self.planning = pd.DataFrame(columns=['Description', 'J', 'date', 'id', 'check'])
        self.tlessons = None
        self.last_day = get_today()
        self.tl.info("New OwnSpacedLearnHub: init done.")

    # Telegram handling
    def send_telegram(self, msg):
        send_text = 'https://api.telegram.org/bot' + str(self.bot_token) + '/sendMessage?chat_id=' \
                    + str(self.chat_id) + '&text=' + str(msg)
        requests.get(send_text)
        return

    def tutorial(self):
        message = "Welcome in this Telegram spaced learning bot !\n"
        message += "It's utility is to help you learning efficiently. For this, you'll have to learn each one "
        message += "of your lesson four times, with a specific interval between each learn session.\n"
        message += "Everyday, at 6am, you'll receive a message summing up what you'll have to learn : "
        message += "the title of the lessons, and their ids.\n"
        message += "Commands:\n"
        message += "- To register a new lesson in the system, you have to send a message with this syntax:\n"
        message += "J0 title_of_lesson\n"
        message += "Ex: J0 Nathan Asie chap 18\n"
        message += "- To mark a lesson as read, you have to send a message with this syntax:\n"
        message += "id_of_lesson done\n"
        message += "Ex: 186 done\n"
        message += "- If you want to delete a lesson, send a message with this syntax:\n"
        message += "id_of_lesson del\n"
        message += "Ex: 389 del\n"
        message += "- To see the lessons you have to learn today, send /today.\n"
        message += "- To see all your lessons, send /list_all.\n"
        message += "\n"
        message += "Good luck !"
        self.send_telegram(message)

    def from_messages_dict_to_list(self, messages: dict):
        if self.chat_id not in list(messages.keys()):
            return
        else:
            return self.from_messages_to_commands(messages[self.chat_id])

    def from_messages_to_commands(self, messages: list):
        for message in messages:
            answer = self.handle_command(str(message))
            if answer is None:
                return
            self.send_telegram(answer)
        return

    def handle_command(self, command: str):
        answer = None
        if command == "/today":
            answer = self.today_message()
            return answer
        elif command == '/start':
            self.tutorial()
            return None
        elif command == '/commands':
            answer = "- To mark a lesson as learnt, send its id + done.\n"
            answer += "Ex: 189 done\n"
            answer += "- To delete a lesson from database, send one of its id + del.\n"
            answer += "Ex: 638 del"
            return answer
        elif command.startswith("J0 "):
            lesson_title = command[2:]
            self.append_new_lesson(lesson_title)
            answer = f"{lesson_title} registered !"
            return answer
        elif " " in list(command) and len(command.split(' ')) == 2 and command.split(' ')[0].isdigit():
            command = command.split(' ')
            _id = int(command[0])
            if _id in list(self.planning.T.loc['id']):
                if command[1] == 'done':
                    self.planning.at[_id, 'check'] = True
                    answer = f"Congratulations for having finished {_id} !"
                    return answer
                elif command[1] == 'del':
                    description = self.planning.at[_id, 'Description']
                    ids_to_delete = self.planning.loc[self.planning['Description'] == description].index
                    for __id__ in list(ids_to_delete):
                        try:
                            self.planning = self.planning.drop(index=__id__)
                        except:
                            self.tl.error(traceback.format_exc())
                            continue
                    answer = f"{description} deleted."
                    return answer
            else:
                answer = "Your answer must respect the syntax:\n"
                answer += "id done\n"
                answer += "Ex: 1396 done"
            return answer
        elif command == "/list_all":
            answer = self.planning
            return answer
        return answer

    # DataFrame and message sending handling
    def gen_id(self):
        new_id = randint(0, 9999)
        if new_id in list(self.planning['id']):
            return self.gen_id()
        else:
            return new_id

    def append_new_lesson(self, description):
        for _day in self.days:
            _id_ = self.gen_id()
            lesson = pd.Series(
                data={
                    'Description': description,
                    'J': _day,
                    'date': _day,
                    'id': _id_,
                    'check': False
                },
                name=_id_)
            self.planning = self.planning.append(lesson)
        return

    def is_new_day(self):
        if get_today() != self.last_day and get_hour() > 5:
            self.last_day = get_today()
            return True
        else:
            return False

    def decrease_date_to_db(self):
        for index in self.planning.index.values:
            self.planning.at[index, 'date'] -= 1
        return

    def today_lessons(self):
        return self.planning.loc[(self.planning['date'] <= 0) & (self.planning['check'] == 0)]

    def today_message(self):
        self.tlessons = self.today_lessons().sort_values(by=['J'])
        if not self.tlessons.index.values:
            message = "Holiday ! No lesson to learn today."
            return message
        message = "Lessons of the day: \n\n"
        for index in self.tlessons.index.values:
            lesson = self.tlessons.T[index]
            message += f"J{lesson['J']} : {lesson['description']} (id: {lesson['id']})\n"
        message += "\nSend 'id done' to mark lesson as learnt."
        return message

    # Run functions
    def run(self):
        if self.is_new_day():
            self.decrease_date_to_db()
            today_message = self.today_message()
            self.send_telegram(today_message)
        return
