import graphene
import bql.schema # local

class Query(bql.schema.Query, graphene.ObjectType):
    """ Combines multiple Query schemas located in different apps """
    pass

schema = graphene.Schema(query=Query)
