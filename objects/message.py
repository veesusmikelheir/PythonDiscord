import asyncio
from .data.message import MessageData
class Message(MessageData):
	def __init__(self,client,id,channel_id,author_id,content,timestamp,tts,mention_everyone,mentions,mention_roles,attachments,embeds,type,webhook_id=None):
		MessageData.__init__(self,
		id=id,
		channel_id=channel_id,
		author_id=author_id,
		content=content,
		timestamp=timestamp,
		tts=tts,
		mention_everyone=mention_everyone,
		mentions=mentions,
		mention_roles=mention_roles,
		attachments = attachments,
		embeds = embeds,
		webhook_id=webhook_id,
		type=type)
		self.client = client

	def from_data(client, data):
		return Message(client,**data.__dict__)

	def from_json(client, json):
		return Message.from_data(client, MessageData.from_json(json))

	def get_channel(self):
		return self.client.get_channel(self.channel_id)

	async def delete(self):
		return await self.get_channel().delete_message(self)

	async def respond(self,content="",tts=False,embed=None,file=None, delete_timer = None):
		message = await self.client.get_channel(self.channel_id).send_message(content,tts,embed,file)
		if not delete_timer:
			return message
		else:
			await asyncio.sleep(delete_timer)
			return await message.delete()

