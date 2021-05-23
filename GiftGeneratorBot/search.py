import requests

from GiftGeneratorBot import UserCriteria
from config import search_url


def searchGift(criteria: UserCriteria):
    link = criteria.link
    if link is None:
        link = "null"
    response = requests.post(search_url,
                      data= {
                          "gender": criteria.gender,
                          "age": criteria.age,
                          "link":  link,
                          "holiday": criteria.holiday,
                          "interests": ', '.join(criteria.interests)
                      })
    result = "Упс, щось пішло не так.\nДавай спробуємо підібрати подарунок заново\nНатискай /start"
    if response.status_code == 200:
        json_response = response.json()
        result = "Знайдені варіанті\n\n"
        for item in json_response['data']:
            result += "Назва: " + item['name'] + '\n'
            result += f"<a href=\"{item['link']}\">Посилання на подарунок</a>\n"
            result += "Ціна: " + str(item['price']) + 'грн\n'
            result += "Рейтинг подарунку: " + str(item['rate']) + '%\n'
            result += "\n"
    return result
