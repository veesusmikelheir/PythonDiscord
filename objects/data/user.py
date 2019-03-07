class UserData:
    def __init__(self,id,username,discriminator,avatar,bot):
        self.id=id
        self.username=username
        self.discriminator=discriminator
        self.avatar=avatar
        self.bot=bot

    def get_mention(self):
        return "<@"+str(self.id)+">"

    def from_json(data):
        return UserData(data["id"],data["username"],data["discriminator"],data["avatar"],data["bot"] if "bot" in data else None)

    def __eq__(self,rhs):
        try:
            return self.id == rhs.user.id
        except:
            try:
                return self.id == rhs.id
            except:
                
                return self.id == rhs


    def __hash__(self):
        return hash(self.id)
