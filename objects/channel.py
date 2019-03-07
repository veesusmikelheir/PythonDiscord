from .data.channel import ChannelData

class Channel(ChannelData):
    def __init__(self,client,id,type,guild_id=None,position=None,permission_overwrites=[],name=None,topic=None,nsfw=None,recipients=None):
        ChannelData.__init__(self,id,type,guild_id,position,permission_overwrites,name,topic,nsfw,recipients)
        self.client = client

    def from_data(client,userdata):
        return Channel(client,**userdata.__dict__)

    def get_guild(self): #TODO: replace this with something more efficient
        if self.type > 0:
            return None

        return self.client.get_guild(self.guild_id)

    async def send_message(self,content="",tts=False,embed=None,file=None):
        return await self.client.send_message(self.id,content,tts,embed,file)

    async def delete_message(self,message):
        try:
            message = message.id
        except:
            pass
        try:
            await self.client.discord_session.gateway.send_discord_request("/channels/"+self.id+"/messages/"+message,method="DELETE")
        except:
            return False
        else:
            return True