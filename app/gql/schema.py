import graphene
from app.neo4j.model import Customer

class CustomerSchema(graphene.ObjectType):
    email = graphene.String()
    name = graphene.String()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.customer = Customer(email=self.email).fetch()

class Query(graphene.ObjectType):
    customer = graphene.Field(lambda: CustomerSchema, email=graphene.String())
    customers = graphene.List(lambda: CustomerSchema)
    all_friends = graphene.List(lambda: CustomerSchema, email=graphene.String())
    distance = graphene.Int(required=True, email=graphene.String(), friend=graphene.String())
    close_friends = graphene.List(lambda:CustomerSchema, email=graphene.String(), distance=graphene.Int())

    def resolve_customer(self, info, email):
        customer = Customer(email=email).fetch()
        return CustomerSchema(**customer.as_dict())
    
    def resolve_customers(self, info):
        return [CustomerSchema(**customer.as_dict()) for customer in Customer().all]
    
    def resolve_all_friends(self, info, email):
        target = Customer(email=email).fetch()
        return [CustomerSchema(**customer.as_dict()) for customer in target.get_friends()]

    def resolve_distance(self, info, **kwargs):
        email = kwargs.get('email')
        friend_email = kwargs.get('friend')
        target = Customer(email=email).fetch()
        friend = Customer(email=friend_email).fetch()
        return target.get_friend_distance(friend)
    
    def resolve_close_friends(self, info, **kwargs):
        email = kwargs.get('email')
        target = Customer(email=email).fetch()
        return target.get_close_friends()
    

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)

    success = graphene.Boolean()
    customer = graphene.Field(lambda: CustomerSchema)

    def mutate(self, info, **kwargs):
        customer = Customer(**kwargs)
        customer.save()

        return CreateCustomer(customer=customer, success=True)

class AddFriends(graphene.Mutation):
    class Arguments:
        customer = graphene.String(required=True)
        friend_email = graphene.String(required=True)
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        customer = Customer(email=kwargs.pop('customer')).fetch()
        customer.add_friends(Customer(email=kwargs.pop('friend_email')).fetch())

        return AddFriends(success=True)

class Mutations(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    add_friends = AddFriends.Field()



schema = graphene.Schema(query=Query, mutation=Mutations, auto_camelcase=False)