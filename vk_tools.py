import vk_api
from datetime import datetime
from vk_api.utils import get_random_id

from config import access_token
from database import Database


class VKTools:
    def __init__(self):
        self.access_token = access_token
        self.vk_session = vk_api.VkApi(token=self.access_token)
        self.vk = self.vk_session.get_api()
        self.database = Database()
        self.database.connect()

    def get_user_info(self, user_id):
        response = self.vk.users.get(user_ids=user_id, fields='bdate,sex,city,relation')
        if response:
            user_info = response[0]
            if all(key in user_info for key in ['bdate', 'sex', 'city', 'relation']):
                age = self.calculate_age(user_info['bdate'])
                sex = user_info['sex']
                city = user_info['city']['title']
                relationship = user_info['relation']
                return age, sex, city, relationship
        return None

    @staticmethod
    def calculate_age(bdate):
        today = datetime.now().date()
        bdate = datetime.strptime(bdate, '%d-%m-%Y').date()
        age = today.year - bdate.year
        if today.month < bdate.month or (today.month == bdate.month and today.day < bdate.day):
            age -= 1
        return age

    def get_users_by_criteria(self):
        criteria = {
            'sex': 2,
            'city': 'Нижний Новгород',
            'age_from': 20,
            'age_to': 30,
            'relationship': 1
        }

        users = []
        count = 0
        offset = 0

        while count < 50:
            response = self.vk.users.search(
                count=50,
                offset=offset,
                **criteria,
                fields='photo_id',
                has_photo=1
            )

            if 'items' in response:
                for item in response['items']:
                    user_info = self.get_user_info(item['id'])
                    if user_info and not self.database.check_user_in_database(user_info[0], item['id']):
                        users.append(item)
                        count += 1
                    if count >= 50:
                        break

                offset += 50
            else:
                break

        return users if users else None

    def get_top_photos(self, users):
        users_with_photos = []
        for user in users:
            response = self.vk.photos.get(owner_id=user['id'], album_id='profile', extended=1)
            if 'items' in response:
                photos = response['items']
                sorted_photos = sorted(photos, key=lambda x: (x['likes']['count'] + x['comments']['count']),
                                       reverse=True)
                user['photos'] = [photo['sizes'][-1]['url'] for photo in sorted_photos[:3]]

            users_with_photos.append(user)

        return users_with_photos

    def send_message(self, user_id, message):
        self.vk.messages.send(
            user_id=user_id,
            message=message,
            random_id=get_random_id()
        )

    def send_result(self, user_id, matched_user, photos):
        message = f'Наилучшее совпадение:\n\n'
        message += f'Имя: {matched_user["first_name"]}\n'
        message += f'Фамилия: {matched_user["last_name"]}\n'
        message += f'Ссылка на профиль: https://vk.com/id{matched_user["id"]}\n'
        message += f'\nФотографии:\n'

        for i, photo in enumerate(photos):
            message += f'Фото {i + 1}: {photo} \n'

        self.send_message(user_id, message)
