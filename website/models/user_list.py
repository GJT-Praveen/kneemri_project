

from flask_login.mixins import UserMixin


class User( UserMixin):

    def __init__(self, name,userid, email, pnumber, password, gender, usertype):
        self.name = name
        self.userid = userid
        self.email = email
        self.pnumber = pnumber
        self.password = password
        self.gender = gender
        self.usertype = usertype

    def get_id(self):
        return self.userid
        
    def get_usertype(self):
        return self.usertype
    
