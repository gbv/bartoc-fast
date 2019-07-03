import graphene
import bartocgraphql.schema # local

class Query(bartocgraphql.schema.Query, graphene.ObjectType):
    """ Combines multiple Query schemas located in different apps """
    pass

schema = graphene.Schema(query=Query)
