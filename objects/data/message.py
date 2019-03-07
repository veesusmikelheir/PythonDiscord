
class MessageData:
    def __init__(self,id,channel_id,author_id,content,timestamp,tts,mention_everyone,mentions,mention_roles,attachments,embeds,type,webhook_id=None):
        self.id=id
        self.channel_id=channel_id
        self.author_id=author_id
        self.content=content
        self.timestamp=timestamp
        self.tts=tts
        self.mention_everyone=mention_everyone
        self.mentions=mentions
        self.mention_roles=mention_roles
        self.attachments = attachments
        self.embeds = embeds
        self.webhook_id=webhook_id
        self.type=type

    def from_json(json):
        return MessageData(
            json["id"],
            json["channel_id"],
            json["author"]["id"],
            json["content"],
            json["timestamp"],
            json["tts"],
            json["mention_everyone"],
            [x["id"] for x in json["mentions"]],
            json["mention_roles"],
            [AttachmentData.from_json(x) for x in json["attachments"]],
            json["embeds"], json["type"],
            json["webhook_id"] if "webhook_id" in json else None)

class AttachmentData:
    def __init__(self,id,filename,size,url,proxy_url,height=None,width=None):
        self.id = id
        self.filename=filename
        self.size=size
        self.url=url
        self.proxy_url=proxy_url
        self.height=height
        self.width=width

    def from_json(json):
        return AttachmentData(**json)

