import telebot
from telebot import types
from config import TOKEN
from UserCriteria import Criteria
import db

bot = telebot.TeleBot(TOKEN)
criteria = Criteria()
interests = { "Sport \U0001F3C3\U0000200D\U00002642\U0000FE0F": True, "Photography \U0001F4F7": True, "Social networks \U0001F4F1": True, "Fashion \U0001F457": True,
             "Travelling \U00002708": True, "Anime \U0001F1F0\U0001F1F7": True, "Music \U0001F3B8": True, "Cinema \U0001F39E": True,  "Comics \U0001F4D6": True,
             "Technology \U0001F4BB": True, "Theater \U0001F3AD": True, "Programming \U0001F468\U0000200D\U0001F4BB": True, "Cosmetics \U0001F484": True,
             "Clothing \U0001F9E5": True, "Modeling \U0001F460": True, "Computer games \U0001F5A5": True, "Fitness \U0001F9D8": True,
             "Animation \U0001F305": True, "Cooking \U0001F958": True, "Education \U0001F4DA": True, "Cars \U0001F697": True, "Animals \U0001F436": True,
             "Wrestling \U0001F93C\U0000200D\U00002642\U0000FE0F": True, "Football \U000026BD": True, "Japan \U0001F1EF\U0001F1F5": True, "BTS \U0001F3B5": True}

holidays = ["Birthday", "New Year", "Valentine's day", "Defender of Ukraine Day", "International Women's Day", "Other"]


@bot.message_handler(commands=['start'])
def start(message):
    userid = message.chat.id
    firstName = message.from_user.first_name
    insertAnswer = db.insert(userid, message.from_user.username, firstName)
    if insertAnswer is True:
        mess = f"Hi, {firstName} \U0001F44B. \n\nI am GiftGeneratorBot \U0001F381\nI'm here to help you choose a gift\n\nSo, let's start choosing the first gift\U0001F609"
        bot.send_message(userid, mess)
    db.updateState(userid, 1)
    criteria.ResetCriteria()
    criteria.SetUserID(userid)
    genderQuestion(userid)


@bot.message_handler(commands=['help'])
def help(message):
    msg = "/start – choose a new gift\n" \
          "/help – *\n" \
          "/share – share me with friends"
    bot.send_message(message.chat.id, msg, parse_mode="html")


@bot.message_handler(commands=['share'])
def shareBot(message):
    link = "https://telegram.me/share/url?url=t.me/GiftsGeneratorBot&text=GiftGeneratorBot%20-%20гарний%20помічник%20у%20сфері%20вибору%20подарунків!%20Вибір%20триває%20декілька%20хвилин!%20Приєднуйся%21"
    msg = f"To quickly <b>share me with friends</b>, click here: <a href=\"{link}\">share</a> . " \
          f"All you have to do is select a chat in Telegram to send information about me. Probably, many other people are also looking for gifts for their friends and family \U0001F609"
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
        bot.send_message(userid, "Sorry, I don't understand that \U0001F614\n"
                                 "To find a gift - click on /start", parse_mode='html',
                         reply_markup=markup)
    elif state == 1:
        if messageText == "For man \U0001F481\U0000200D\U00002642\U0000FE0F":
            criteria.SetGender("Man")
        elif messageText == "For woman \U0001F481\U0000200D\U00002640\U0000FE0F":
            criteria.SetGender("Woman")
        elif messageText == "Other \U00002B50":
            criteria.SetGender("Other")
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
        if messageText == "Skip":
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
        if messageText[:-2] == "Find" and len(criteria.interests) != 0:
            db.updateState(userid, 0)
            resetInterests()
            # Test Code
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            startButton = types.KeyboardButton("/start")
            markup.row(startButton)
            bot.send_message(userid, "To find a gift again - click on /start", parse_mode='html', reply_markup=markup)
            # Test Code
        else:
            if interests.get(messageText) is not None:
                criteria.AddInterests(messageText[:-2])
                interests[messageText] = False
                interestQuestion(userid)
            elif messageText[:-2] == "Find" and len(criteria.interests) == 0:
                errorMessage(userid, mode="interest-empty")
                interestQuestion(userid)
            else:
                errorMessage(userid)
                interestQuestion(userid)


def genderQuestion(userid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
    btn1 = types.KeyboardButton("For man \U0001F481\U0000200D\U00002642\U0000FE0F")
    btn2 = types.KeyboardButton("Other \U00002B50")
    btn3 = types.KeyboardButton("For woman \U0001F481\U0000200D\U00002640\U0000FE0F")
    markup.add(btn1, btn2, btn3)
    bot.send_message(userid, "Who are you picking a gift for?", parse_mode='html', reply_markup=markup)


def ageQuestion(userid):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(userid, "How old is he/she?", parse_mode='html', reply_markup=markup)


def linkQuestion(userid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    skipButton = types.KeyboardButton("Skip")
    markup.row(skipButton)
    bot.send_message(userid, "Does he/she use social media?\U0001F4F1\n- If <b>yes</b>, you can leave a link to the Facebook or Twitter page."
                             "\n- If <b>no</b>, click the button below\U0001F447", parse_mode='html', reply_markup=markup)


def holidayQuestion(userid):
    lastRow = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    firstButton = types.KeyboardButton("Birthday \U0001F382")
    secondButton = types.KeyboardButton("New Year \U0001F384")
    thirdButton = types.KeyboardButton("Valentine's day \U0001F496")
    fourthButton = types.KeyboardButton("Defender of Ukraine Day \U0001F396")
    fifthButton = types.KeyboardButton("International Women's Day \U0001F490")
    sixthButton = types.KeyboardButton("Other \U00002B50")
    markup.row(firstButton, secondButton)
    if criteria.gender == "Man":
        markup.row(thirdButton, fourthButton)
    elif criteria.gender == "Woman":
        markup.row(thirdButton, fifthButton)
    else:
        markup.row(thirdButton, fourthButton)
        markup.row(fifthButton, sixthButton)
        lastRow = False
    if lastRow is True:
        markup.row(sixthButton)
    bot.send_message(userid, "What's the occasion for a gift?", parse_mode='html', reply_markup=markup)


def interestQuestion(userid, first = False):
    markup = interestsMarkup()
    if first is True:
        bot.send_message(userid, "What are his/her interests?\nYou can choose several options", parse_mode='html', reply_markup=markup)
    elif len(criteria.interests) != 0:
        msg = "You have chosen the following interests "
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
    markup.add(types.KeyboardButton("Find \U0001F50E"))
    return markup


def errorMessage(userid, mode="default"):
    errmsg = "Sorry, I don't understand that \U0001F614\n" \
             "Can you choose one of the options below?\U0001F447\n" \
             "If you don't see them, then click on the icon with four squares there \U0001F643"
    if mode == "age-outside":
        errmsg = "Sorry, but you must indicate the age in the range from 1 to 100 \U0001F614"
    elif mode == "age-not-int":
        errmsg = "Sorry, you probably didn't indicate the age.\nPlease indicate the age as a one number \U0001F522"
    elif mode == "interest-empty":
        errmsg = "In order to find the suitable gift, you need to choose at least one of  interests \U0001F3AE"
    elif mode == "external-link":
        errmsg = "Sorry, but I can only analyze the social networks Facebook and Twitter so far.\n" \
                 "If there is no page, then I suggest you skip this step\U00002935"
    bot.send_message(userid, errmsg, parse_mode='html')


def checkLink(link):
    if link.find("facebook") != -1 or link.find("twitter.com") != -1:
        return True
    return False


bot.polling()


