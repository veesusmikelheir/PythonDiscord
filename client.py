from .objects.user import User
from .objects.guild import Guild
from .objects.channel import Channel
import json
import re
class DiscordClient:
    """Holds data about the current session and guilds, as well as providing an interface for 'active' (non data only) discord objects"""
    def __init__(self,session):
        self.discord_session = session
        self.user=None
        self.guilds = {} #convert these to dictionaries to make searching faster at some point
        self.direct_channels=[] 

    def add_proto_guild(self,guild_data):
        if guild_data.id in self.guilds:
            del self.guilds[guild_data.id]
        self.guilds[guild_data.id]=Guild.from_data(self,guild_data)

    def try_add_channel(self,channel_data):
        print(json.dumps(channel_data,indent = 4,default = lambda o: o.__dict__))
        if channel_data.type>0:
            for i in [x for x in self.direct_channels if x.id==channel_data.id]:
                self.direct_channels.remove(i)
                print("Deleted duplicate channel")
            self.direct_channels.append(Channel.from_data(self,channel_data))
        else:
            self.get_guild(channel_data.guild_id).add_or_replace_channel(Channel.from_data(self,channel_data))
    
    def get_guild(self, id=None,name=None,regex=None):
        if not regex:
            if id:
                if id in self.guilds:
                    return self.guilds[id]
                else:
                    return None
            for x in self.guilds.values():
                if x.name==name:
                    return x
            return None

        pattern = re.compile(regex)
        for x in self.guilds.values():
            if pattern.match(x.name):
                return x
        return None

    def get_channel(self, id=None,name=None):
        for i in self.guilds.values():
            chan = i.get_channel(id,name)
            if chan:
                return chan
        if not id:
            return None
        for i in self.direct_channels:
            if i.id == id:
                return i
        return None




    async def send_message(self,channel_id,content="",tts=False,embed=None,file=None):
        return await self.discord_session.gateway.send_message(channel_id,content,tts,embed,file)


