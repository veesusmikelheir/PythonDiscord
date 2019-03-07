from .data.guild import GuildData
from .channel import Channel
class Guild(GuildData):
    def __init__(self,client,id,name,icon,splash,owner_id,roles = [],emojis=[],member_count = 0,members=[],channels=[]):#,presences = []):
        GuildData.__init__(self,
        id=id,
        name=name,
        icon=icon,
        splash=splash,
        owner_id=owner_id,
        roles=roles,
        emojis=emojis,
        member_count=member_count,
        members=members,
        channels=channels)
        self.client = client

    def from_data(client,userdata):
        guild = Guild(client,**userdata.__dict__)
        guild.channels = SuperChannelList([Channel.from_data(client,x) for x in guild.channels])
        return guild

class SuperChannelList(list):
    def __getitem__(self,index):
        if isinstance(index,str):
            return self.get_channel(index)
        else:
            return list.__getitem__(self,index)
    def get_channel(self,id):
        if id:
            for i in self:
                if i.id==id or i.name==id:
                    print(i.name+" "+id)
                    return i
        return None 