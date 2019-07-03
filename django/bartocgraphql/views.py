import json
import graphene

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import BasicForm # local
from .schema import Query    # local

def index(request):
    """ Index resp. landing page """
    return render(request, 'bartocgraphql/index.html')
   
def basic(request):
    """ Basic search for non-expert users """

    if request.method == 'GET':         # if the form is submitted
        form = BasicForm(request.GET)   # create a form instance and populate it with data from the request    
        if form.is_valid():
            searchword = form.cleaned_data["searchword"] # https://docs.djangoproject.com/en/2.2/ref/forms/api/#django.forms.Form.cleaned_data
            query_string = """{
    resultsGlobal(searchword: "!!!SEARCHWORD!!!", category: 0) {
    uri
    prefLabel
    altLabel
    hiddenLabel
    definition
  }
}"""
            query_string = query_string.replace("!!!SEARCHWORD!!!", searchword)
            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string)       # https://docs.graphene-python.org/en/latest/_modules/graphql/execution/base/#ExecutionResult
            result_pretty = json.dumps(result.data, sort_keys=True, indent=4)
            return HttpResponse(result_pretty,content_type="application/json")
    else:
        form = BasicForm()
    return render(request, 'bartocgraphql/basic.html', {'form': form})

def data(request):
    """ Data retrieval """

    if request.method == 'GET':         # if the form is submitted
        form = BasicForm(request.GET)   # create a form instance and populate it with data from the request 
        if form.is_valid():
            searchword = form.cleaned_data["searchword"] # https://docs.djangoproject.com/en/2.2/ref/forms/api/#django.forms.Form.cleaned_data
            query_string = """{
    resultsGlobal(searchword: "!!!SEARCHWORD!!!", category: 0) {
    uri
    prefLabel
    altLabel
    hiddenLabel
    definition
  }
}"""
            query_string = query_string.replace("!!!SEARCHWORD!!!", searchword)
            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string)       # https://docs.graphene-python.org/en/latest/_modules/graphql/execution/base/#ExecutionResult
            result_pretty = json.dumps(result.data, sort_keys=True, indent=4)
            return HttpResponse(result_pretty,content_type="application/json")
    else:
        form = BasicForm()
    return render(request, 'bartocgraphql/data.html', {'form': form})
