from django.urls import path
from graphene_django.views import GraphQLView

from . import views

urlpatterns = [
    path('', views.index, name='index'),                                # landing page
    path('about', views.about, name='about'),                           # about page
    path('advanced', views.advanced, name='advanced'),                  # advanced search
    path('expert', GraphQLView.as_view(graphiql=True),name='expert'),   # expert view
    path('data', views.data, name='data'),                              # data output
]
