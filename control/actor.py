from definitions import ActorType, ActionType

class Actor:
    """
    Abstract representation of an actor
    """

    def __init__(self, name: str = None, actortype: ActorType = None, uid: str = None, output = None):
        self.name = name
        self.type = actortype
        self.uid = uid
        # nr. of output in case of multiple outputs, 0 else
        self.output = output

    def get_actor_name(self) -> str:
        return self.name
        
    def set_actor_name(self, name: str) -> None:
        self.name = name
    
    def get_actor_type(self) -> ActorType:
        return self.type

    def set_actor_type(self, actortype: ActorType) -> None:
        self.type = actortype

    def get_uid(self) -> str:
        return self.uid 

    def set_uid(self, uid: str) -> None:
        self.uid = uid 

    def get_output(self):
        return self.output

    def set_output(self, output) -> None:
        self.output = output
