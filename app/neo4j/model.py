from py2neo import Graph
from py2neo.ogm import GraphObject, Property, Related
from py2neo.data import walk
from app import settings
import random, math

graph = Graph(
    host=settings.NEO4J_HOST,
    port=settings.NEO4J_PORT,
    user=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD,
)

class BaseModel(GraphObject):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def all(self):
        return self.match(graph)

    def save(self):
        graph.push(self)

class Customer(BaseModel):
    __primarykey__ = 'email'

    name = Property()
    email = Property()

    friends = Related('Customer', 'IS_FRIENDS_WITH')

    def as_dict(self):
        return {
            'email': self.email,
            'name': self.name,
        }
    
    def fetch(self):
        customer = self.match(graph, self.email).first()
        return customer

    def add_friends(self, friend):
        distance = random.randrange(50)

        self.friends.add(friend,
                        {
                            'distance': distance
                        })
        self.save()
    
    def get_friends(self):
        return self.friends
    
    def get_friend_distance(self, friend):
        return self.friends.get(friend, 'distance')

    def get_close_friends(self):
        customer = self.match(graph, self.email).first().__node__
        rels = graph.relationships.match({customer, None}, "IS_FRIENDS_WITH").where(f"_.distance <= 25")
        friends = [Customer.wrap(rel.start_node) if rel.start_node != customer else Customer.wrap(rel.end_node) for rel in rels]
        return friends