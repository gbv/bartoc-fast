from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import BasicForm # local

def index(request):
    """ Landing page """
    return render(request, 'skosmos/index.html')
   
def basic(request):
    """ Basic search for non-expert users """

    if request.method == 'GET':         # if the form is submitted

        form = BasicForm(request.GET)   # create a form instance and populate it with data from the request
        
        if form.is_valid():
            # searchword = form.cleaned_data
            # here graphql is called to compute the results
            
            return HttpResponseRedirect('https://www.yahoo.com/search/') # redirect to page displaying results

    else:
        form = BasicForm()

    return render(request, 'hero/basic.html', {'form': form})


#def results(request):
#    return HttpResponse("Search results")
