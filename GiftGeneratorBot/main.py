import telebot
from telebot import types
from config import TOKEN
from UserCriteria import Criteria
import db

bot = telebot.TeleBot(TOKEN)
criteria = Criteria()
interests = { "Спорт \U000026BD": True, "Фотографія \U0001F4F7": True, "Соціальні мережі \U0001F4F1": True, "Мода \U0001F457": True,
             "Подорожі \U00002708": True, "Аніме \U0001F1F0\U0001F1F7": True, "Музика \U0001F3B8": True, "Кіно \U0001F39E": True,  "Комікси \U0001F4D6": True,
             "Технології \U0001F5A5": True }
holidays = ["День народження", "Новий рік", "День закоханих", "14 жовтня", "8 березня", "Інше"]


@bot.message_handler(commands=['start'])
def start(message):
    userid = message.chat.id
    firstName = message.from_user.first_name
    insertAnswer = db.insert(userid, message.from_user.username, firstName)
    if insertAnswer is True:
        mess = f"Привіт, {firstName} \U0001F44B. \n\nЯ - GiftGeneratorBot \U0001F381\nТепер я твій власний помічник у виборі подарунків.\n\nОтже, почнемо обирати перший подарунок\U0001F609"
        bot.send_message(userid, mess)
    db.updateState(userid, 1)
    criteria.ResetCriteria()
    criteria.SetUserID(userid)
    genderQuestion(userid)


@bot.message_handler(commands=['help'])
def help(message):
    msg = "/start – обрати новий подарунок\n" \
          "/help – допомога\n" \
          "/share – розповісти про бота друзям"
    bot.send_message(message.chat.id, msg, parse_mode="html")


@bot.message_handler(commands=['share'])
def shareBot(message):
    link = "https://telegram.me/share/url?url=t.me/GiftsGeneratorBot&text=GiftGeneratorBot%20-%20гарний%20помічник%20у%20сфері%20вибору%20подарунків!%20Вибір%20триває%20декілька%20хвилин!%20Приєднуйся%21"
    msg = f"Щоб швидко та зручно <b>розповісти про мене друзям</b>, натискай сюди: <a href=\"{link}\">share</a> . " \
          f"Залишиться лише обрати чат у Телеграмі, кому ти хочеш надіслати інформацію про мене. Імовірно, багато інших людей також шукають подарунки своїм знайомим та близьким \U0001F609"
    bot.send_message(message.chat.id, msg, parse_mode="html")


@bot.message_handler(func=lambda message: True)
def chooseState(message):
    userid = message.chat.id
    state = db.getUserState(userid)
    messageText = message.text
    if state == 0:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        startButton = types.KeyboardButton("/start")
        markup.row(startButton)
        bot.send_message(userid, "Вибач, я так не розумію \U0001F614\n"
                                 "Щоб підібрати подарунок - натискай на /start", parse_mode='html',
                         reply_markup=markup)
    elif state == 1:
        if messageText == "Чоловіку \U0001F481\U0000200D\U00002642\U0000FE0F":
            criteria.SetGender("Чоловік")
        elif messageText == "Жінці \U0001F481\U0000200D\U00002640\U0000FE0F":
            criteria.SetGender("Жінка")
        elif messageText == "Інша \U00002B50":
            criteria.SetGender("Інша")
        else:
            errorMessage(userid)
            genderQuestion(userid)
            return
        db.updateState(userid, state + 1)
        ageQuestion(userid)
    elif state == 2:
        try:
            age = int(messageText)
            if 0 < age < 101:
                criteria.SetAge(age)
                db.updateState(userid, state + 1)
                linkQuestion(userid)
            else:
                errorMessage(userid, "age-outside")
                ageQuestion(userid)
        except Exception as e:
            errorMessage(userid, "age-not-int")
            ageQuestion(userid)
    elif state == 3:
        if messageText == "Пропустити":
            db.updateState(userid, state + 1)
            holidayQuestion(userid)
        elif checkLink(messageText) is True:
            criteria.SetLink(messageText)
            db.updateState(userid, state + 1)
            holidayQuestion(userid)
        elif checkLink(messageText) is False:
            errorMessage(userid, "external-link")
        else:
            errorMessage(userid)
            linkQuestion(userid)
    elif state == 4:
        try:
            index = holidays.index(messageText[:-2])
            holiday = holidays[index]
            criteria.SetHoliday(holiday)
            db.updateState(userid, state + 1)
            interestQuestion(userid, first=True)
        except Exception as e:
            errorMessage(userid)
            holidayQuestion(userid)
    elif state == 5:
        if messageText[:-2] == "Знайти" and len(criteria.interests) != 0:
            db.updateState(userid, 0)
            resetInterests()
            # Test Code
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            startButton = types.KeyboardButton("/start")
            markup.row(startButton)
            bot.send_message(userid, "Щоб ще раз підібрати подарунок - натискай на /start", parse_mode='html', reply_markup=markup)
            # Test Code
        else:
            if interests.get(messageText) is not None:
                criteria.AddInterests(messageText[:-2])
                interests[messageText] = False
                interestQuestion(userid)
            elif messageText[:-2] == "Знайти" and len(criteria.interests) == 0:
                errorMessage(userid, mode="interest-empty")
                interestQuestion(userid)
            else:
                errorMessage(userid)
                interestQuestion(userid)


def genderQuestion(userid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Чоловіку \U0001F481\U0000200D\U00002642\U0000FE0F")
    btn2 = types.KeyboardButton("Інша \U00002B50")
    btn3 = types.KeyboardButton("Жінці \U0001F481\U0000200D\U00002640\U0000FE0F")
    markup.add(btn1, btn2, btn3)
    bot.send_message(userid, "Кому ти обираєш подарунок?", parse_mode='html', reply_markup=markup)


def ageQuestion(userid):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(userid, "Скільки років цій людині?", parse_mode='html', reply_markup=markup)


def linkQuestion(userid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    skipButton = types.KeyboardButton("Пропустити")
    markup.row(skipButton)
    bot.send_message(userid, "Ця людина користується соціальними мережами?\U0001F4F1\n- Якщо <b>так</b>, то можете залишити посилання на "
                             "сторінку Facebook або Twitter.\n- Якщо <b>ні</b>, то натисніть кнопку нижче\U0001F447", parse_mode='html', reply_markup=markup)


def holidayQuestion(userid):
    lastRow = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    firstButton = types.KeyboardButton("День народження \U0001F382")
    secondButton = types.KeyboardButton("Новий рік \U0001F384")
    thirdButton = types.KeyboardButton("День закоханих \U0001F496")
    fourthButton = types.KeyboardButton("14 жовтня \U0001F396")
    fifthButton = types.KeyboardButton("8 березня \U0001F490")
    sixthButton = types.KeyboardButton("Інше \U00002B50")
    markup.row(firstButton, secondButton)
    if criteria.gender == "Чоловік":
        markup.row(thirdButton, fourthButton)
    elif criteria.gender == "Жінка":
        markup.row(thirdButton, fifthButton)
    else:
        markup.row(thirdButton, fourthButton)
        markup.row(fifthButton, sixthButton)
        lastRow = False
    if lastRow is True:
        markup.row(sixthButton)
    bot.send_message(userid, "З якої нагоди даруєш подарунок?", parse_mode='html', reply_markup=markup)


def interestQuestion(userid, first = False):
    markup = interestsMarkup()
    if first is True:
        bot.send_message(userid, "Які у людини інтереси?\nМожна обрати декілька варіантів", parse_mode='html', reply_markup=markup)
    elif len(criteria.interests) != 0:
        msg = "Ви обрали такі інтереси: "
        for interest in interests:
            if interests[interest] is False:
                msg += interest + ", "
        msg = msg[:-2]
        bot.send_message(userid, msg, parse_mode='html', reply_markup=markup)


def resetInterests():
    for interest in interests:
        interests[interest] = True


def interestsMarkup():
    buttons = []
    i = -1
    count = 0
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for interest in interests:
        if interests[interest] is True:
            button = types.KeyboardButton(interest)
            if count % 2 == 0:
                buttons.append([])
                i += 1
            buttons[i].append(button)
            count += 1
    for i in range(len(buttons)):
        if len(buttons[i]) == 2:
            markup.row(buttons[i][0], buttons[i][1])
        elif len(buttons[i]) == 1:
            markup.row(buttons[i][0])
    markup.add(types.KeyboardButton("Знайти \U0001F50E"))
    return markup


def errorMessage(userid, mode="default"):
    errmsg = "Вибачте, я вас не розумію \U0001F614\n" \
             "Можете обрати один із варіантів знизу?\U0001F447\n" \
             "Якщо ви їх не бачите, то натисніть там на іконку з чотирма квадратиками \U0001F643"
    if mode == "age-outside":
        errmsg = "Вибачте, але необхідно вказати вік у діапазоні від 1 до 100 \U0001F614"
    elif mode == "age-not-int":
        errmsg = "Вибачте, скоріше за все ви не вказали вік.\nБудь ласка вкажіть вік одним числом \U0001F522"
    elif mode == "interest-empty":
        errmsg = "Для того, щоб підібрати відповідні подарунки, необхідно вибрати хоча б один інтерес людини \U0001F3AE"
    elif mode == "external-link":
        errmsg = "Вибачте, але я поки можу аналізувати соціальні мережі Facebook та Twitter.\n" \
                 "Якщо немає сторінки, то пропоную вам пропустити даний етап\U00002935"
    bot.send_message(userid, errmsg, parse_mode='html')


def checkLink(link):
    if link.find("facebook") != -1 or link.find("twitter.com") != -1:
        return True
    return False


bot.polling()
