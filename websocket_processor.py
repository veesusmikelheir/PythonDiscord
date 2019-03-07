import asyncio
import aiohttp
from aiohttp import WSMsgType
import json

class WebsocketProcessor:
	def __init__(self,gateway):
		self.gateway=gateway
		self.websocket=None
		self.received_heartbeat=False
		self.sequence_number = None

	async def connect_websocket(self):
		url = await self.get_websocket_url()
		self.websocket = await self.gateway.session.ws_connect(url)
		self.received_heartbeat=False
		self.session_id=None

	async def disconnect(self):
		if self.websocket:
			await self.websocket.close()

	async def initial_handshake(self):
		hello = deserialize_payload(await self.websocket.receive_json())
		print(hello)
		self.received_heartbeat=True
		return self.heart_beat_loop(hello.data["heartbeat_interval"])

	async def identify(self):
		await self.send_payload(self.create_default_identity())
		payload = deserialize_payload(await self.websocket.receive_json())
		print(payload)
		self.session_id = payload.data["session_id"]
		return payload

	async def process_handshake_keepers(self,payload):
		if payload.opcode==1:
			await self.send_heartbeat()
			print("got heartbeat request")
			return True
		elif payload.opcode==11:
			print("got a heartbeat ACK!")
			self.received_heartbeat=True
			return True
		return False


	async def process_event_payload(self,payload):
		if not payload.opcode==0:
			return
		self.sequence_number=payload.seq
		await self.gateway.process_incoming_event(payload.event,payload.data)

	async def try_resume(self):
		if(self.session_id==None):
			return False
		await self.send_payload(Payload(6,data={
			"token":self.gateway.discord.auth_token,
			"session_id":self.session_id,
			"seq":self.sequence_number
			}))
		async for msg in self.websocket:
			payload = message_to_payload(msg)
			if payload.opcode == 9:
				print("RESUME FAILED")
				return False
			elif payload.opcode == 0:
				print("RESUMING")
				if payload.event == "RESUME":
					return True

				await process_event_payload(payload)

	async def processing_loop(self):
		async for msg in self.websocket:
						
			payload = message_to_payload(msg)

			if(await self.process_handshake_keepers(payload)):
				continue;

			if payload.opcode==0:
				await self.process_event_payload(payload)
			elif payload.opcode == 7:
				return "reconnect"
			else:
				print("got a "+str(payload))

		return "no_ack"
					
	async def start_websocket(self):
		heartbeat_future = None
		try:
			while True:
				try:
					await self.connect_websocket()
					heartbeat_future = asyncio.ensure_future(await self.initial_handshake())
					if not await self.try_resume():
						await self.gateway.on_websocket_reset()
						await self.gateway.initialize_local_data(await self.identify())

					await self.processing_loop()


				except ValueError as e:
					raise e
				except SocketCloseException as e:	
					print("SOCKET CLOSE EXCEPTION!")
					raise e
		finally:
			if not heartbeat_future == None:
				heartbeat_future.cancel()
			if not self.websocket.closed:
				await self.websocket.close()

	async def heart_beat_loop(self,timeout):
		while not self.websocket.closed:
			await asyncio.sleep(timeout/1000.0)
			if not self.received_heartbeat:
				print("got no heartbeat ack, closing and reconnect...")
				await self.websocket.close(close=4009)
				return
			self.received_heartbeat=False
			print("sending heartbeat...")
			await self.send_heartbeat()
		

	async def send_payload(self,payload):
		await self.websocket.send_json(payload.serialize_payload())

	async def send_heartbeat(self):
		await self.send_payload(Payload(1,data=self.sequence_number))

	def create_default_identity(self,online_mode = None):
		if online_mode == None:
			online_mode={
				"game":{
					"name":"Botting Around...",
					"type":0
				},	
				"status":"online",
				"afk":False
			}
		return Payload(2,data={
				"token":self.gateway.discord.auth_token,
				"properties":{
					"$os":"linux",
					"$browser":"discord",
					"$device":"discord"
				},
				"presence":online_mode
			})

	async def get_websocket_url(self):
		return (await self.gateway.send_discord_request("/gateway/bot"))["url"]
		
def deserialize_payload(payload):
	seq = None
	event = None
	if payload["op"] == 0:
		seq = payload["s"]
		event = payload["t"]
	return Payload(payload["op"],payload["d"],event,seq)

def raise_on_msg_error(msg):
	if msg.type==WSMsgType.ERROR:
		raise ValueError("Web Socket Error: "+str(msg.type)+" "+str(msg.extra))
	elif msg.type==WSMsgType.CLOSE:
		raise SocketCloseException(msg)

def message_to_payload(msg):
	raise_on_msg_error(msg)
	return deserialize_payload(msg.json())

class Payload:
	def __init__(self,opcode,data,event=None,seq=None):
		self.opcode = opcode
		self.data = data
		self.event=event
		self.seq = seq

	def serialize_payload(self):
		payload = {"op":self.opcode,"d":self.data}
		return payload

	def __str__(self):
		string = "Payload{Op: "+str(self.opcode)
		if self.opcode == 0:
			string=string+" Event: "+self.event+" Seq: "+str(self.seq)
		string = string+"}"
		return string

class SocketCloseException(Exception):
	def __init__(self,msg):
		close_code = int(msg.extra)
		Exception.__init__(self,"Socket Closed On Code: "+msg.extra)
		self.close_code = close_code
