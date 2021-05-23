import requests

from GiftGeneratorBot import UserCriteria
from config import search_url
from config import upcoming_holidays


def searchGift(criteria: UserCriteria):
    link = criteria.link
    if link is None:
        link = "null"
    response = requests.post(search_url,
                             data={
                                 "gender": criteria.gender,
                                 "age": criteria.age,
                                 "link": link,
                                 "holiday": criteria.holiday,
                                 "interests": ', '.join(criteria.interests)
                             })
    result = "Упс, щось пішло не так.\nДавай спробуємо підібрати подарунок заново\nНатискай /start"
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


def checkHolidays():
    response = requests.post(upcoming_holidays,
                             data={
                                 "email": ""
                             })
    if response.status_code == 200:
        json_response = response.json()
        if len(json_response['data']['holidays']) == 0:
            return None
        result = "Вибачте за це повідомлення\U0001F64F, я не можу допустити того, щоб ви пропустили одразу декілька важливих свят\U0001F389 і ваші близькі залишилися без подаруночків\U0001F381\n"
        for item in json_response['data']['holidays']:
            day = ""
            if 1 < item[0] < 5:
                day = f"залишилося {item[0]} дні"
            elif item[0] == 0 or item[0] == 5:
                day = f"залишилося {item[0]} днів"
            elif item[0] == 1:
                day = f"залишився {item[0]} день"
            for holiday in item[1]:
                result += f"\n\U0001F538До \"{holiday['name']}\" {day}."
        result += "\nПоквапся\U00002757\nЯ з радістю допоможу тобі з вибором\U00002764"
        print(result)
        return result
    return None
