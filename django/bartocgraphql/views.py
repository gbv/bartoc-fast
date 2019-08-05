""" views.py """

from typing import List, Set, Dict, Tuple, Optional, Union

import json
import graphene

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import BasicForm, AdvancedForm  
from .models import SkosmosInstance, SparqlEndpoint
from .schema import Query                   
from .utility import DEF_MAXSEARCHTIME, DEF_DUPLICATES, DEF_DISABLED

QUERYSTRING = '''{
    resultsGlobal(SEARCHWORD, MAXSEARCHTIME, DUPLICATES, DISABLED) {
    uri
    prefLabel
    altLabel
    hiddenLabel
    definition
    source
  }
}'''

def index(request: HttpRequest) -> HttpResponse:
    """ Landing page """
    
    context = {'landing_page': 'active'}
    return render(request, 'bartocgraphql/index.html', context)

def about(request: HttpRequest) -> HttpResponse:
    """ About page """

    federation = list(SparqlEndpoint.objects.all()) + list(SkosmosInstance.objects.all()) # perhaps a FEDERATION constant in models or utility?
    federation.sort(key=lambda x: x.name, reverse=False)

    context = {'about_page': 'active', 'federation': federation}
    return render(request, 'bartocgraphql/about.html', context)

def feedback(request: HttpRequest) -> HttpResponse:
    """ About page """

    context = {'feedback_page': 'active'}
    return render(request, 'bartocgraphql/feedback.html', context)

def basic(request: HttpRequest) -> HttpResponse:
    """ Basic search for non-expert users """

    if request.method == 'GET':         
        form = BasicForm(request.GET)
        if form.is_valid():
            
            query_string = parse(form)

            print(f'-->START') # dev
            print(query_string) # dev

            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string)

            results = result.data.get('resultsGlobal') # we just need the values of 'resultsGlobal'
            arguments = form.cleaned_data
            context = {'basic_page': 'active', 'results': results, 'arguments': arguments} 
            return render(request, 'bartocgraphql/results.html', context)
    else:
        form = BasicForm()
    context = {'form': form, 'basic_page': 'active'}
    return render(request, 'bartocgraphql/basic.html', context)

def advanced(request: HttpRequest) -> HttpResponse:
    """ Advanced search """

    if request.method == 'GET':                             
        form = AdvancedForm(request.GET)        
        if form.is_valid():

            query_string = parse(form)

            print(f'-->START') # dev
            print(query_string) # dev

            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string)

            results = result.data.get('resultsGlobal') # we just need the values of 'resultsGlobal'
            arguments = form.cleaned_data
            context = {'advanced_page': 'active', 'results': results, 'arguments': arguments} 
            return render(request, 'bartocgraphql/results.html', context)
    else:
        form = AdvancedForm()
    context = {'form': form, 'advanced_page': 'active'}
    return render(request, 'bartocgraphql/advanced.html', context)

def data(request: HttpRequest) -> HttpResponse:
    """ Data retrieval """

    if request.method == 'GET':         
        form = AdvancedForm(request.GET)   
        if form.is_valid():

            query_string = parse(form)
            
            print(f'-->START') # dev
            print(query_string) # dev
 
            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string)
            
            result_pretty = json.dumps(result.data, sort_keys=True, indent=4)
            return HttpResponse(result_pretty, content_type='application/json')
    else:
        form = AdvancedForm()
    context = {'form': form, 'data_page': 'active'}
    return render(request, 'bartocgraphql/data.html', context)

def parse(form: Union[BasicForm, AdvancedForm]) -> str:
    """ Update QUERYSTRING with arguments from form (if any) or default values """

    query_string = QUERYSTRING

    # searchword:
    searchword = form.cleaned_data['searchword'] 
    query_string = query_string.replace('SEARCHWORD', f'searchword: "{searchword}"')                          

    # maxsearchtime:
    try:
        maxsearchtime = form.cleaned_data['maxsearchtime']
        assert maxsearchtime is not None
    except (KeyError, AssertionError):
        form.cleaned_data['maxsearchtime'] = DEF_MAXSEARCHTIME # pass to context
        query_string = query_string.replace('MAXSEARCHTIME', f'maxsearchtime: {DEF_MAXSEARCHTIME}') # no form option (see basic)
    else:
        query_string = query_string.replace('MAXSEARCHTIME', f'maxsearchtime: {maxsearchtime}') # form option on/off (see advanced)

    # duplicates:
    try:
        duplicates = form.cleaned_data['duplicates']
    except KeyError:
        form.cleaned_data['duplicates'] = DEF_DUPLICATES # context
        query_string = query_string.replace(', DUPLICATES', f', duplicates: {str(DEF_DUPLICATES).lower()}') # no form option
    else:
        query_string = query_string.replace(', DUPLICATES', f', duplicates: {str(duplicates).lower()}') # form option on/off

    # disabled resources:
    try:
        disabled = form.cleaned_data['disabled']
    except KeyError:
        form.cleaned_data['disabled'] = DEF_DISABLED # context
        query_string = query_string.replace(', DISABLED', f', disabled: {DEF_DISABLED}') # no form option
    else:
        disabled = str(disabled).replace('\'', '"')
        query_string = query_string.replace(', DISABLED', f', disabled: {disabled}') # form option on/off      

    # category:
    # category = form.cleaned_data['category']

    return query_string
    



