import vk_api
import datetime
from vk_api.utils import get_random_id
from config import group_token, access_token

class VKTools:
    def __init__(self, access_token):
        self.access_token = access_token
        self.vk_session = vk_api.VkApi(token=self.access_token)
        self.vk = self.vk_session.get_api()

    def get_user_info(self, user_id):
        user_info = self.vk.users.get(user_id=user_id, fields='bdate,sex,city,relation')

        if user_info:
            user_info = user_info[0]
            age = self.calculate_age(user_info['bdate'])
            sex = user_info['sex']
            city = user_info['city']['title'] if 'city' in user_info else None
            relationship = user_info['relation']
            return age, sex, city, relationship
        else:
            return None

    def calculate_age(self, bdate):
        today = datetime.datetime.now().date()
        bdate = datetime.datetime.strptime(bdate, '%d.%m.%Y').date()
        age = today.year - bdate.year
        if today.month < bdate.month or (today.month == bdate.month and today.day < bdate.day):
            age -= 1
        return age

    def get_users_by_criteria(self, criteria):
        users = self.vk.users.search(
            count=50,
            sex=criteria['sex'],
            city=criteria['city'],
            age_from=criteria['min_age'],
            age_to=criteria['max_age'],
            status=criteria['relationship'],
            fields='photo_id',
            has_photo=1
        )
        return users['items'] if 'items' in users else None

    def get_top_photos(self, user_id):
        photos = self.vk.photos.get(
            owner_id=user_id,
            album_id='profile',
            extended=1
        )
        if 'items' in photos:
            sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'] + x['comments']['count'], reverse=True)
            top_photos = sorted_photos[:3]
            return top_photos
        else:
            return None

    def send_message(self, user_id, message):
        self.vk.messages.send(
            user_id=user_id,
            message=message,
            random_id=get_random_id()
        )

    def send_photos(self, user_id, photos):
        for photo in photos:
            photo_url = f'photo{photo["owner_id"]}_{photo["id"]}'
            attachment.append(photo_url)

        self.vk.messages.send(
            user_id=user_id,
            attachment=','.join(attachments),
            random_id=get_random_id()
        )