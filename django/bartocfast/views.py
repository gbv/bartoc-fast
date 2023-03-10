""" views.py """

from typing import List, Set, Dict, Tuple, Optional, Union
from collections import OrderedDict
from datetime import datetime

import json
import graphene

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import BasicForm, AdvancedForm  
from .models import Federation, SkosmosInstance, SparqlEndpoint, LobidResource
from .schema import Query, Helper                   
from .utility import VERSION, DEF_MAXSEARCHTIME, DEF_DUPLICATES, DEF_DISABLED, LOCAL_APP_PATH, Entry

QUERYSTRING = '''{
    results(SEARCHWORD, MAXSEARCHTIME, DUPLICATES, DISABLED) {
    uri
    prefLabel
    altLabel
    hiddenLabel
    definition
    source
  }
}'''

def index(request: HttpRequest) -> HttpResponse:
    """ Landing page including basic search for non-expert users """

    if request.method == 'GET':         
        form = BasicForm(request.GET)
        if form.is_valid():
            
            query_string = parse(form)

            print(f'-->START') # dev
            print(query_string) # dev

            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string, context_value="basic")

            results_id = "https://bartoc-fast.ub.unibas.ch/bartocfast/?" + request.GET.urlencode()
            log(results_id)
           
            try:
                results = result.data.get('results') # we just need the values of 'results'
            except AttributeError:  # in case there are no results:
                results = None
                print("views.index: AttributeError: invalid search string!")
        
            arguments = form.cleaned_data
            requests = gather_requests(form)
            requests.sort(key=lambda x: x.name.upper(), reverse=False)
            context = {'landing_page': 'active', 'version': VERSION, 'results': results, 'arguments': arguments, 'requests': requests} 
            return render(request, 'bartocfast/results.html', context)
    else:
        form = BasicForm()
    
    context = {'form': form, 'landing_page': 'active', 'version': VERSION}
    return render(request, 'bartocfast/index.html', context)

def about(request: HttpRequest) -> HttpResponse:
    """ About page """

    federation = federation = Federation.objects.all()[0]
    resources = Helper.make_display_resources()
    resources.sort(key=lambda x: x.name.upper(), reverse=False)

    context = {'about_page': 'active', 'version': VERSION, 'federation': federation, 'resources': resources}
    return render(request, 'bartocfast/about.html', context)

def advanced(request: HttpRequest) -> HttpResponse:
    """ Advanced search """

    if request.method == 'GET':
        form = AdvancedForm(request.GET) 

        if form.is_valid():

            query_string = parse(form)

            print(f'-->START') # dev
            print(query_string) # dev

            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string, context_value="advanced")

            results_id = "https://bartoc-fast.ub.unibas.ch/bartocfast/advanced?" + request.GET.urlencode()
            log(results_id)

            try:
                results = result.data.get('results') 
            except AttributeError:  
                results = None
                print("views.advanced: AttributeError: invalid search string!")

            arguments = form.cleaned_data
            requests = gather_requests(form)
            requests.sort(key=lambda x: x.name.upper(), reverse=False)
            context = {'advanced_page': 'active', 'version': VERSION, 'results': results, 'arguments': arguments, 'requests': requests}

            return render(request, 'bartocfast/results.html', context)

        else:
            form = AdvancedForm({'maxsearchtime': DEF_MAXSEARCHTIME, 'disabled': Helper.make_display_disabled()})
    else:
        form = AdvancedForm()

    context = {'form': form, 'advanced_page': 'active', 'version': VERSION}
    return render(request, 'bartocfast/advanced.html', context)

def api(request: HttpRequest) -> HttpResponse:
    """ API """

    if request.method == 'GET':         
        form = AdvancedForm(request.GET)
        
        if form.is_valid():

            query_string = parse(form)

            print(f'-->START') # dev
            print(query_string) # dev
 
            schema = graphene.Schema(query=Query)
            result = schema.execute(query_string, context_value="api")

            results_id = "https://bartoc-fast.ub.unibas.ch/bartocfast/api?" + request.GET.urlencode()
            log(results_id)

            jsonld = make_jsonld(make_context(form, results_id), result.data)
            jsonld_pretty = json.dumps(jsonld, indent=4)

            return HttpResponse(jsonld_pretty, content_type='application/json')
        
        else:
            form = AdvancedForm({'maxsearchtime': DEF_MAXSEARCHTIME, 'disabled': Helper.make_display_disabled()})
    else:
        form = AdvancedForm()
        
    context = {'form': form, 'api_page': 'active', 'version': VERSION}
    return render(request, 'bartocfast/api.html', context)

def parse(form: Union[BasicForm, AdvancedForm]) -> str:
    """ Update QUERYSTRING with arguments from form (if any) or default values """
    
    query_string = QUERYSTRING

    # searchword:
    searchword = form.cleaned_data['searchword']
    query_string = query_string.replace('SEARCHWORD', f'searchword: "{searchword}"')                          

    # maxsearchtime:
    try:
        maxsearchtime = form.cleaned_data['maxsearchtime']
    except KeyError:
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

def gather_requests(form: Union[BasicForm, AdvancedForm]) -> List[Entry]:
    """ Gather all requests sent to resources """

    if type(form) == BasicForm:
            resources = Helper.make_resources()
            try:
                disabled = form.cleaned_data['disabled'][:]
                resources = Helper.remove_disabled(resources, disabled)
            except KeyError:
                pass 
    else:
        try:
            disabled = form.cleaned_data['disabled'][:]
        except KeyError:
            pass
        else: # dev: needs to be generalized
            if "Research-Vocabularies-Australia" in disabled:
                resources = Helper.make_resources()
                disabled.remove("Research-Vocabularies-Australia")
                resources = Helper.remove_disabled(resources, disabled)
            else:
                resources = Helper.make_resources()
                resources = Helper.remove_disabled(resources, disabled)
                resources = resources + Helper.make_slaves()
  
    searchword = form.cleaned_data['searchword']
    requests = []
    for resource in resources:
        query = resource.select(0) # category
        request = resource.construct_request(searchword, query)
        requests.append(Entry(resource.name, request))
    return requests

def make_context(form: AdvancedForm, results_id: str) -> OrderedDict:
    """ Make a JSON-LD @context based on form """

    resources = Helper.make_resources()

    try:
        disabled = form.cleaned_data['disabled'][:]
    except KeyError:
        pass
    else: # dev: needs to be generalized
        if "Research-Vocabularies-Australia" in disabled:
            resources = Helper.make_resources()
            disabled.remove("Research-Vocabularies-Australia")
            resources = Helper.remove_disabled(resources, disabled)
        else:
            resources = Helper.make_resources()
            resources = Helper.remove_disabled(resources, disabled)
            resources = resources + Helper.make_slaves()

    context = OrderedDict()
    context.update( { "skos" : "http://www.w3.org/2004/02/skos/core#" } )

    for resource in resources:
        context.update( { resource.name : resource.url } )
    
    context.update( { "results" : { "@id": results_id,
                                    "@type" : "@id",
                                    "@container" : "@set" }
                      } )

    context.update( { "altLabel" : "skos:altLabel",
                      "definition" : "skos:definition",
                      "hiddenLabel" : "skos:hiddenLabel",
                      "prefLabel" : "skos:prefLabel",
                      "source" : "skos:ConceptScheme",
                      "uri" : "@id"
                      } )

    return context

def make_jsonld(context: OrderedDict, results: OrderedDict) -> OrderedDict:
    """ Join @context and results to produce a JSON-LD """
    
    jsonld = OrderedDict()
    jsonld.update( { "@context" : context } )
    jsonld.update(results)
    return jsonld

def log(url: str) -> None:
    """ Add url with timestamp to logging database """

    now = (datetime.now()).strftime("%Y:%m:%d:%H:%M:%S\n")
    urlnow = url + "@" + now
    
    path = LOCAL_APP_PATH + "/logs/queries.txt"
    file = open(path, "a")
    file.write(urlnow)
