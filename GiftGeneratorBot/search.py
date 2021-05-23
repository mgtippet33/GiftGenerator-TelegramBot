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
    result = "Упс, щось пішло не так.\U0001F614\nДавай спробуємо підібрати подарунок заново\U0001F501"
    if response.status_code == 200:
        json_response = response.json()
        result = "\U0001F539Знайдені варіанти:\n\n"
        for item in json_response['data']:
            result += "\U0001F538Назва: " + item['name'] + '\n'
            result += f"<a href=\"{item['link']}\">\U0001F517Посилання на подарунок</a>\n"
            result += "\U0001F4B5Ціна: " + str(item['price']) + 'грн\n'
            result += "\U0001F4F6Рейтинг подарунку: " + str(item['rate']) + '%\n'
            result += "\n"
    return result
