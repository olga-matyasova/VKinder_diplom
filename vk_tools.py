import pprint
import vk_api
from vk_api.exceptions import ApiError
from datetime import datetime
from vk_api.utils import get_random_id
from config import access_token

class VkTools:
    def __init__(self, access_token):
        self.access_token = access_token
        self.vk_session = vk_api.VkApi(token=self.access_token)
        self.vk = self.vk_session.get_api()

    def get_user_info(self, user_id):
        try:
            user_info, = self.vk.method('users.get', {'user_id':user_id, 'fields':'bdate,sex,city,relation'})
        except ApiError as e:
            user_info = {}
            print('Ошибка при получении информации о пользователе: ', e)
        result = {
            'name': f'{user_info["first_name"]} {user_info["last_name"]}' if
            ('first_name' in user_info) and ('last_name' in user_info) else None,
            'sex': user_info.get('sex'),
            'city': user_info['city']['title'] if
            ('city' in user_info) and (user_info.get('city') is not None)
            else None,
            'age': datetime.now().year - int(user_info['bdate'].split('.')[2]) if
            ('bdate' in user_info) and (user_info.get("bdate") is not None)
            else None
        }
        return result

    def search_worksheet(self, criteria, offset=0):
        try:
            sex = 1 if criteria['sex'] == 2 else 2
            city = criteria['city']
            current_year = datetime.now().year
            user_year = int(criteria['bdate'].split('.')[2])
            age = current_year - user_year
            age_from = age - 5
            age_to = age + 5

            users = self.vk.method('users.search', {
                'count': 50,
                'offset': offset,
                'sex': sex,
                'city': city,
                'age_from': age_from,
                'age_to': age_to,
                'status': 6,
                'is_closed': False
            })

            users = users['items']
        except KeyError as e:
            print(f'Ошибка при получении информации о пользователе: {e}')
            return []
        except ApiError as e:
            print(f'Ошибка API VK: {e}')
            return []

        result = []
        for user in users:
            if not user['is_closed']:
                result.append({
                    'id': user['id'],
                    'name': user['first_name'] + ' ' + user['last_name']
                })

        return result

    def get_photos(self, user_id):
        try:
            photos = self.vk.method('photos.get', {'user_id': user_id, 'album_id': 'profile', 'extended': 1})
        except ApiError as e:
            print(f'Ошибка API VK: {e}')
            return []

        try:
            photos = photos.get('items', [])
        except AttributeError as e:
            print(f'Ошибка при получении списка фотографий: {e}')
            return []

        result = []

        for photo in photos:
            try:
                owner_id = photo.get('owner_id')
                photo_id = photo.get('id')
                likes_count = photo.get('likes', {}).get('count', 0)
                comments_count = photo.get('comments', {}).get('count', 0)

                result.append({
                    'owner_id': owner_id,
                    'id': photo_id,
                    'likes': likes_count,
                    'comments': comments_count,
                })
            except KeyError as e:
                print(f'Ошибка при обработке фотографии: {e}')

        result.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)

        return result[:3]


if __name__ =='__main__':
    user_id = 147917628
    vk_tools = VkTools(access_token)
    criteria = vk_tools.get_user_info(user_id)
    users = vk_tools.search_worksheet(criteria,50)
    users = users.pop()
    photos = vk_tools.get_photos(users['id'])
    pprint(users)
