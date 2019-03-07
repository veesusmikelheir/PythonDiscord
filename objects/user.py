from .data.user import UserData

class User(UserData):
    def __init__(self,client,uid,username,discriminator,avatar,bot):
        UserData.__init__(self,uid,username,discriminator,avatar,bot)
        self.client = client

    def from_data(client,userdata):
        return User(client,*userdata.__dict__.values())

    def from_json(client,json):
        return User.from_data(client,UserData.from_json(json))