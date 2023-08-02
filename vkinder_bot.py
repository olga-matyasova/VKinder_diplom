import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.exceptions import ApiError
from vk_api.utils import get_random_id
from datetime import datetime

from config import group_token, access_token, DATABASE_URL
from vk_tools import VkTools
from database import Database

vk_tools = VkTools(access_token)
database = Database()
database.connect()

class VkinderBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=group_token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.group_token = group_token
        self.access_token = access_token
        self.criteria = {}
        self.users = []
        self.offset = 0
        self.vk_tools = VkTools(access_token)

    def send_message(self, user_id, message, attachments=None):
        try:
            self.vk.messages.send(
                user_id=user_id,
                message=message,
                attachment=attachments,
                random_id=get_random_id()
            )
        except ApiError as e:
            print('Ошибка при отправке сообщения: ', e)

    def send_photos(self, user_id, photos):
        attachment = []
        for photo in photos:
            photo_url = f'photo{photo["owner_id"]}_{photo["id"]}'
            attachment.append(photo_url)

        try:
            self.vk.messages.send(
                user_id=user_id,
                attachment=','.join(attachment),
                random_id=get_random_id()
            )
        except ApiError as e:
            print('Ошибка при отправке фотографии: ', e)

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.lower()
                user_id = event.user_id

                if request == 'привет':
                    self.criteria = self.vk_tools.get_user_info(user_id)
                    self.send_message(user_id=user_id,
                                     message='Привет! Я VKinder. Отправь сообщением "поиск" для подбора второй половинки.',
                                     random_id=0)
                elif request.startswith('поиск'):
                    criteria = request[6:]
                    users = self.vk_tools.search_worksheet(criteria)
                    self.send_message(user_id=user_id,
                                      message=f'Найдено {users["count"]} пользователей.',
                                      random_id=0)

                    if users:
                        user_ids = [str(user['id']) for user in users]
                        matched_user_id = self.vk_tools.search_worksheet(criteria, offset=0)

                        if matched_user_id:
                            user_info = self.vk.users.get(user_ids=[matched_user_id], fields='bdate, sex, city, relation')
                            user = user_info[0]
                            age = datetime.now().year - int(user['bdate'].split('.')[2])
                            sex = user['sex']
                            city = user['city']['title']
                            relation = user['relation']

                            self.send_message(user_id=user_id,
                                            message=f'Наилучший вариант для тебя:\nВозраст: {age}\nПол: {sex}\nГород: {city}\nОтношения: {relation}',
                                            random_id=0)

                            self.vk_tools.get_photos(matched_user_id)
                            self.send_photos(user_id, photos)

                            if not database.check_result(user_id, matched_user_id):
                                database.save_result((user_id, matched_user_id))
                            else:
                                pass

                        else:
                            self.send_message(user_id=user_id, message='К сожалению, не удалось найти подходящих пользователей.',
                                             random_id=0)

                    else:
                        self.send_message(user_id=user_id, message='Не удалось выполнить поиск. Попробуйте снова.',
                                 random_id=0)

                else:
                    self.send_message(user_id=user_id, message='Я вас не понимаю.', random_id=0)

if __name__ == '__main__':
    VkinderBot().event_handler()
