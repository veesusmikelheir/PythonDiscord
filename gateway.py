import asyncio
import aiohttp
from .websocket_processor import WebsocketProcessor
from .objects.user import User
import json
from .objects.data.guild import GuildData
from .objects.data.message import MessageData
from .objects.message import Message
from .objects.data.channel import ChannelData
from .objects.channel import Channel
from .callbacks import MessageCallbackContext, ChannelCallbackContext
discord_url = "https://discordapp.com/api/v6/"

class DiscordGateway:
	def __init__(self,discord):
		self.discord = discord
		self.session=None
		self.websocket = WebsocketProcessor(self)
		self.proto_guilds = set()
	async def connect(self):

		self.session = aiohttp.ClientSession()
		try:
			await self.websocket.start_websocket()
		finally:
			await self.disconnect()

	async def disconnect(self):
		await self.websocket.disconnect()
		await self.session.close()

	async def send_discord_request(self,endpoint, headers = {}, data=None, params=None, method = "GET",is_multipart=False):
		if endpoint[0] == '/':
			endpoint = endpoint[1:]
		if endpoint[-1]== '/':
			endpoint = endpoint[:-1]
		endpoint = discord_url+endpoint
		headers["Authorization"] = self.discord.auth_token
		headers["User-Agent"]="DiscordBot (veesusbot, 0.0.1)"
		async with self.session.request(method,endpoint,headers = headers,params = params,json = data if not is_multipart else None, data = data if is_multipart else None)  as resp:
			resp.raise_for_status()
			try:
				return await resp.json()
			except aiohttp.client_exceptions.ContentTypeError:
				return await resp.text()

	async def on_ready(self):
		await self.discord.callbacks.on_ready()

	async def on_message_create(self,json_data):
		if json_data["author"]["id"] == self.discord.client.user.id:
			return
		if "webhook_id" in json_data:
			return
		if "bot" in json_data["author"] and json_data["author"]["bot"]:
			return
		message = Message.from_json(self.discord.client,json_data)
		message = MessageCallbackContext(message,self.discord.client.get_guild(json_data["guild_id"]) if "guild_id" in json_data else None)
		await self.discord.callbacks.on_message_create(message)
		#guild = MessageData.from_json(json_data)
		#print(json.dumps(guild,indent=4,default = lambda o: o.__dict__))

	async def on_channel_create(self,json):
		channel = ChannelData.from_json(json)
		self.discord.client.try_add_channel(channel)

	async def on_message_delete(self,json_data):
		await self.discord.callbacks.on_message_delete(ChannelCallbackContext(self.discord.client.get_channel(json_data["channel_id"])),json_data["id"])

 

	async def on_websocket_reset(self):
		self.discord.client.guilds.clear()
		self.discord.client.direct_channels.clear()

	async def process_incoming_event(self,event_name,data):
		if(event_name=="GUILD_CREATE"):
			guild = GuildData.from_json(data)
			self.discord.client.add_proto_guild(guild)
			if len(self.proto_guilds)>0:
				uid = data["id"]
				if uid in self.proto_guilds:
					self.proto_guilds.remove(uid)
					if len(self.proto_guilds)==0:
						await self.on_ready()

		elif(event_name=="MESSAGE_CREATE"):
			await self.on_message_create(data)
		elif(event_name=="MESSAGE_DELETE"):
			await self.on_message_delete(data)
		elif(event_name=="CHANNEL_CREATE"):
			await self.on_channel_create(data)
		elif(event_name!="PRESENCE_UPDATE"):
			print(event_name)

		pass

	async def initialize_local_data(self,ready_payload):
		self.discord.client.user = User.from_json(self.discord.client,ready_payload.data["user"])
		self.proto_guilds=set([x["id"] for x in ready_payload.data["guilds"]])



	async def send_message(self,channel_id,content="",tts=False,embed=None,file=None):

		if not content and not embed and not file:
			raise ValueError("Tried to send empty message content!")
		data = {"content":content,"tts":tts}
		if embed:	
			data["embed"]=embed
		multipart = {"payload_json":json.dumps(data)}
		if file:
			multipart["file"]=file

		payload = await self.send_discord_request("channels/"+channel_id+"/messages",method="POST",data=multipart,is_multipart=True)
		try:
			return Message.from_json(self.discord.client,payload)
		except:
			return payload