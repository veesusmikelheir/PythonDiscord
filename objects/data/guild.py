from .user import UserData
from .role import RoleData
from .emoji import EmojiData
from .channel import ChannelData

class GuildData:
	def __init__(self,id,name,icon,splash,owner_id,roles = [],emojis=[],member_count = 0,members=[],channels=[]):#,presences = []):
		self.id=id
		self.name=name
		self.icon=icon
		self.splash=splash
		self.owner_id=owner_id
		self.roles=roles
		self.emojis=emojis
		self.member_count=member_count
		self.members=members
		self.channels=channels

	def from_json(json):
		def optional(key):
			return json[key] if key in json else None
		def optional_list(key,decoder):
			return [decoder(x) for x in json[key]] if key in json else []
		return GuildData(
			json["id"],
			json["name"],json["icon"],
			json["splash"],json["owner_id"],
			list(reversed(sorted(optional_list("roles",RoleData.from_json),key=lambda x:x.position))),
			optional_list("emojis",EmojiData.from_json),
			optional("member_count"),
			{i.user.id:i for i in optional_list("members",GuildUserData.from_json)},
			sorted(optional_list("channels",ChannelData.from_json),key = lambda o: o.position))
	def get_member(self,id):
		if id in self.members:
			return self.members[id]
		return None
	def get_channel(self,id=None,name=None):
		if id:
			for i in self.channels:
				if i.id==id:
					return i
			return None
		elif name:
			for i in self.channels:
				if i.name==name:
					return i
			return None
		return None 
	def add_or_replace_channel(self,channel):
		for i in [x for x in self.channels if x.id==channel.id]:
			self.channels.remove(i)
		channels.append(channel)
	def __eq__(self,rhs):
		try:
			return self.id==rhs.id
		except:
			return self.id==rhs

class GuildUserData:
	def __init__(self,user,nick=None,roles=[]):
		self.user = user
		self.nick = nick
		self.roles = roles

	def from_json(json):
		return GuildUserData(UserData.from_json(json["user"]),json["nick"] if "nick" in json else None,json["roles"])

	def __eq__(self,rhs):
		try:
			return self.user.id == rhs.user.id
		except:
			try:
				return self.user.id == rhs.id
			except:
				return self.user.id == rhs


class GuildPresenceData:
	def __init__(self, id, roles=[],guild_id = None):
		self.id=id
		self.roles = roles
		self.guild_id = guild_id

	def from_json(json):
		return GuildPresenceData(json["user"]["id"],[RoleData.from_json(x) for x in json["roles"]],json["guild_id"])	