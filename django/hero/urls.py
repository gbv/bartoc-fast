from django.urls import path
from graphene_django.views import GraphQLView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('basic', views.basic, name='basic'), # basic search
    path('expert', GraphQLView.as_view(graphiql=True),name='expert'), # expert view
    # path('data', ???), # data output
    # path('results', views.results, name='results'), # basic search results
    
]
