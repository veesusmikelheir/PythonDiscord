import asyncio
from .gateway import DiscordGateway
from .client import DiscordClient
from .callbacks import DiscordCallbacksHandler
class DiscordSession:
	def __init__(self):
		self.loop = asyncio.get_event_loop()
		self.auth_token=None
		self.gateway = DiscordGateway(self)
		self.client = DiscordClient(self)
		self.callbacks = DiscordCallbacksHandler()

	def connect(self,auth_token):
		self.auth_token=auth_token
		try:
			self.loop.run_until_complete(self.gateway.connect())
		finally:
			self.loop.run_until_complete(self.disconnect())
	async def disconnect(self):
		await self.gateway.disconnect()
