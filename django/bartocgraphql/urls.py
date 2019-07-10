from django.urls import path
from graphene_django.views import GraphQLView

from . import views

urlpatterns = [
    path('', views.index, name='index'),                                # landing page
    path('about', views.about, name='about'),                           # about page
    path('feedback', views.feedback, name='feedback'),                  # feedback page
    path('basic', views.basic, name='basic'),                           # basic search
    path('advanced', views.advanced, name='advanced'),                  # advanced search
    path('expert', GraphQLView.as_view(graphiql=True),name='expert'),   # expert view
    path('data', views.data, name='data'),                              # data output
]
