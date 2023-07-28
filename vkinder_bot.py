import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import group_token, access_token
from vk_tools import VKTools
from database import Database

vk_tools = VKTools(access_token)
database = Database()
database.connect()

vk_session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = event.user_id

        if request == 'привет' or request == '/start':
            vk.messages.send(user_id=user_id,
                             message='Привет! Я VKinder. Отправь сообщением поиск для подбора второй половинки.',
                             random_id=0)

        elif request.startswith('поиск'):
            criteria = request[6:]
            users = vk_tools.get_users_by_criteria(criteria)

            if users:
                user_ids = [str(user['id']) for user in users]
                result = vk_tools.get_best_match(user_id, user_ids)

                if result:
                    matched_user_id = result[0]
                    age, sex, city, relationship = vk_tools.get_user_info(matched_user_id)
                    top_photos = vk_tools.get_top_photos(matched_user_id)

                    vk.messages.send(user_id=user_id,
                                     message=f'Наилучший вариант для тебя:\nВозраст: {age}\nПол: {sex}\nГород: {city}\nОтношения: {relationship}',
                                     random_id=0)
                    vk_tools.send_photos(user_id, top_photos)

                    database.save_result((user_id, matched_user_id))

                else:
                    vk.messages.send(user_id=user_id, message='К сожалению, не удалось найти подходящих пользователей.',
                                     random_id=0)
            else:
                vk.messages.send(user_id=user_id, message='Не удалось выполнить поиск. Попробуйте снова.', random_id=0)

        else:
            vk.messages.send(user_id=user_id, message='Я вас не понимаю.', random_id=0)
if __name__ == '__main__':
    vkinder_bot = VKTools(access_token)
    vkinder_bot.run()