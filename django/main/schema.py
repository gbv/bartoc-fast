import graphene
import bartocfast.schema # local

class Query(bartocfast.schema.Query, graphene.ObjectType):
    """ Combines multiple Query schemas located in different apps """
    pass

schema = graphene.Schema(query=Query)
