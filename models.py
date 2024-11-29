users = []

class User:
    def __init__(self, id, username, password, email="", picture=""):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.picture = picture

    @classmethod
    def find_by_username(cls, username):
        return next((user for user in users if user.username == username), None)

    @classmethod
    def find_by_id(cls, id):
        return next((user for user in users if user.id == id), None)
