class EmojiData:
    def __init__(self,id,name=None):
        self.id=id
        self.name=name

    def from_json(json):
        return EmojiData(json["id"],json["name"])