import json
import graphene

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import BasicForm, AdvancedForm  # local
from .schema import Query                   # local

QUERYSTRING = '''{
    resultsGlobal(SEARCHWORD, MAXSEARCHTIME, DUPLICATES) {
    uri
    prefLabel
    altLabel
    hiddenLabel
    definition
    source
  }
}'''

def index(request):
    """ Landing page """
    
    context = {'landing_page': 'active'}
    return render(request, 'bartocgraphql/index.html', context)

def about(request):
    """ About page """

    context = {'about_page': 'active'}
    return render(request, 'bartocgraphql/about.html', context)

def feedback(request):
    """ About page """

    context = {'feedback_page': 'active'}
    return render(request, 'bartocgraphql/feedback.html', context)
   
def basic(request):
    """ Basic search for non-expert users """

    if request.method == 'GET':         
        form = BasicForm(request.GET)
        if form.is_valid():
            
            query_string = QUERYSTRING
            searchword = form.cleaned_data['searchword']
            query_string = query_string.replace('SEARCHWORD', f'searchword: "{searchword}"')
            query_string = query_string.replace(', MAXSEARCHTIME', '')

            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string) 
            result_pretty = json.dumps(result.data, sort_keys=True, indent=4)
            return HttpResponse(result_pretty,content_type='application/json')
    else:
        form = BasicForm()
    context = {'form': form, 'basic_page': 'active'}
    return render(request, 'bartocgraphql/basic.html', context)

def data(request):
    """ Data retrieval """

    if request.method == 'GET':         
        form = BasicForm(request.GET)   
        if form.is_valid():
            pass
    else:
        form = BasicForm()
    context = {'form': form, 'data_page': 'active'}
    return render(request, 'bartocgraphql/data.html', context)

def advanced(request):
    """ Advanced search """

    if request.method == 'GET':                             
        form = AdvancedForm(request.GET)        
        if form.is_valid():

            query_string = QUERYSTRING # copy since we need the original
            
            searchword = form.cleaned_data['searchword'] # https://docs.djangoproject.com/en/2.2/ref/forms/api/#django.forms.Form.cleaned_data
            query_string = query_string.replace('SEARCHWORD', f'searchword: "{searchword}"')                          

            maxsearchtime = form.cleaned_data['maxsearchtime']
            if maxsearchtime == None:
                query_string = query_string.replace(', MAXSEARCHTIME', '')
            else:
                query_string = query_string.replace('MAXSEARCHTIME', f'maxsearchtime: {maxsearchtime}')

            duplicates = form.cleaned_data['duplicates']
            query_string = query_string.replace(', DUPLICATES', f', duplicates: {str(duplicates).lower()}')
            print(f'-->START') # dev
            print(query_string)

            # category = form.cleaned_data['category']
                
            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string) # https://docs.graphene-python.org/en/latest/_modules/graphql/execution/base/#ExecutionResult
            result_pretty = json.dumps(result.data, sort_keys=True, indent=4)
            return HttpResponse(result_pretty, content_type='application/json')
    else:
        form = AdvancedForm()
    context = {'form': form, 'advanced_page': 'active'}
    return render(request, 'bartocgraphql/advanced.html', context)

