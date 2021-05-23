class Criteria:
    def __init__(self):
        self.userid = None
        self.gender = None
        self.age = None
        self.link = None
        self.holiday = None
        self.interests = []

    def SetUserID(self, userid):
        self.userid = userid

    def SetGender(self, gender):
        self.gender = gender

    def SetAge(self, age):
        self.age = age

    def SetLink(self, link):
        self.link = link

    def SetHoliday(self, holiday):
        self.holiday = holiday

    def AddInterests(self, interest):
        self.interests.append(interest)

    def ResetCriteria(self):
        self.userid = None
        self.gender = None
        self.age = None
        self.link = None
        self.holiday = None
        self.interests = []