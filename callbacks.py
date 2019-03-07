class DiscordCallbacksHandler:
    def __init__(self):
        self.callback_objs = []


    def add_callbacks(self, callback):
        self.callback_objs.append(callback)

    def remove_callbacks(self,callback):
        if callback in self.callback_objs:
            self.callback_objs.remove(callback)

    async def on_message_create(self,message):
        for i in self.callback_objs:
            if hasattr(i,"on_message_create"):
                await i.on_message_create(message)

    async def on_message_delete(self,channel,id):
        for i in self.callback_objs:
            if hasattr(i,"on_message_delete"):
                await i.on_message_delete(channel,id)
    async def on_ready(self):
        for i in self.callback_objs:
            if hasattr(i,"on_ready"):
                await i.on_ready()

class Context:
    def __init__(self,wrapped,dictvals):
        self.wrapped = wrapped
        self.dictvals = dictvals

    def __getattr__(self,attr):
        if attr in self.dictvals:
            return self.dictvals[attr]
        if attr == "dictvals" or attr=="wrapped":
            return getattr(self,attr)
        return getattr(self.wrapped,attr)
    def __setattr__(self,attr,val):
        if attr=="dictvals" or attr=="wrapped":
            object.__setattr__(self,attr,val)
        else:
            setattr(self.wrapped,attr,val)

class CallbackContext(Context):
    def __init__(self,wrapped,dictvals,client):
        dictvals["gateway"] = client.discord_session.gateway
        dictvals["send_discord_request"] = client.discord_session.gateway.send_discord_request
        dictvals["http_session"] = client.discord_session.gateway.session
        Context.__init__(self,wrapped,dictvals)


class MessageCallbackContext(CallbackContext):
    def __init__(self,wrapped,guild=None):
        channel = wrapped.get_channel() if not guild else guild.get_channel(wrapped.channel_id)
        dictvals ={
            "channel":channel,
        }
        guild = channel.get_guild() if not guild else guild
        if guild:
            dictvals["guild"]=guild
        CallbackContext.__init__(self,wrapped,dictvals,wrapped.client)

class ChannelCallbackContext(CallbackContext):
    def __init__(self,wrapped):
        guild = wrapped.get_guild()
        dictvals={}
        if guild:
            dictvals["guild"]=guild
        CallbackContext.__init__(self,wrapped,dictvals,wrapped.client)


