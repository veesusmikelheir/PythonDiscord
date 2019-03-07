from .user import UserData
class ChannelData:
    def __init__(self,id,type,guild_id=None,position=None,permission_overwrites=[],name=None,topic=None,nsfw=None,recipients=None):
        self.id=id
        self.type=type
        self.guild_id=None
        self.position=position
        self.permission_overwrites=permission_overwrites
        self.name=name
        self.topic=topic
        self.nsfw=nsfw
        self.recipients=recipients

    def from_json(json):
        def optional(key):
            return json[key] if key in json else None
        return ChannelData(json["id"],json["type"],optional("guild_id"),optional("position"),[PermissionOverwriteData.from_json(x) for x in json["permission_overwrites"]] if "permission_overwrites" in json else [],optional("name"),optional("topic"),optional("nsfw"),[UserData.from_json(x) for x in json["recipients"]] if "recipients" in json else None)


class PermissionOverwriteData:
    def __init__(self,id,overwrite_type,allow,deny):
        self.id=id
        self.type=overwrite_type
        self.allow=allow
        self.deny=deny

    def from_json(json):
        return PermissionOverwriteData(json["id"],json["type"],json["allow"],json["deny"])
