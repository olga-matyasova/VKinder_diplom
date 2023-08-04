import vk_api 
from vk_api import longpoll 
from vk_api.longpoll import VkLongPoll, VkEventType 
  
import config 
import database 
import vk_tools 
from config import group_token, access_token 
from vk_tools import VKTools 
from database import Database 
  
def main(database=None, longpoll=None): 
    database.connect() 
    vk_session = vk_api.VkApi(token=config.group_token) 
    vk = vk_session.get_api() 
    vk_tools = VKTools(access_token) 
    database = Database() 
    daatabase.connect() 
    database.create_table() 
    longpoll = longpoll.VkLongPoll(vk_session) 
    
    for event in longpoll.listen(): 
     
        if event.type == VkEventType.MESSAGE_NEW and event.to_me: 
        request = event.text.lower() 
        user_id = event.user_id 
  
            if request == 'привет' or request == '/start': 
                vk_tools.send_message(user_id, 'Привет! Я VKinder. Отправь сообщением "поиск" для подбора второй половинки.') 
  
            elif request.startswith('поиск'): 
            criteria = vk_tools.get_criteria(user_id) 
                if criteria: 
                    users = vk_tools.get_users_by_criteria(criteria) 
  
                    if users: 
                        best_match = None 
                        for user in users: 
                            best_match = user 
                            break 
  
                        if best_match: 
                            top_photos = vk_tools.get_top_photos(best_match['id']) 
                        vk_tools.send_result(user_id, best_match, top_photos) 
                            database.save_result((user_id, best_match['id'])) 
                        else:
                            vk_tools.send_message(user_id, 'К сожалению, не удалось найти подходящих пользователей.') 
                    else: 
                        vk_tools.send_message(user_id, 'К сожалению, не удалось найти подходящих пользователей.') 
                else: 
                    vk_tools.send_message(user_id, 'Не удалось получить критерии поиска.') 
            else: 
                vk_tools.send_message(user_id, 'Я вас не понимаю.') 
  
  
if __name__ == '__main__': 
     main()