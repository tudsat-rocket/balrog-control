from definitions import ActorType, ActionType

class Actor:
    """
    Abstract representation of an actor
    """

    def __init__(self, actor_id: int, name: str = None, 
                 actortype: ActorType = ActorType.DUMMY, uid: str = None, output: int = 0):
        
        # actor identifier 
        self.id = actor_id 
        # human readable name 
        self.name = name
        self.type = actortype
        # uid of bricklet responsible for controlling the actor 
        self.br_uid = uid
        # nr. of output in case of multiple outputs, 0 else
        self.output = output

    def get_id(self) -> int: 
        return self.id 

    def get_actor_name(self) -> str:
        return self.name
        
    def set_actor_name(self, name: str) -> None:
        self.name = name
    
    def get_actor_type(self) -> ActorType:
        return self.type

    def set_actor_type(self, actortype: ActorType) -> None:
        self.type = actortype

    def get_br_uid(self) -> str:
        return self.br_uid 

    def set_br_uid(self, uid: str) -> None:
        self.br_uid = uid 

    def get_output(self):
        return self.output

    def set_output(self, output) -> None:
        self.output = output

