class RoleData:
	def __init__(self,id,name,color,hoist,position,permissions,managed,mentionable):
		self.id = id
		self.name = name
		self.color = color
		self.hoist = hoist
		self.position = position
		self.permissions = permissions
		self.managed = managed
		self.mentionable=mentionable

	def from_json(json):
		return RoleData(json["id"],json["name"],json["color"],json["hoist"],json["position"],json["permissions"],json["managed"],json["mentionable"])



	def __eq__(self,p2):
		return self.id==p2.id

	def __hash__(self):
		return hash(self.id)