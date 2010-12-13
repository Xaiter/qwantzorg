from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from comics.forms import CreateAccountForm, CreateComicForm, RequestPasswordResetForm, PasswordResetForm
from comics.models import Comic, User, UserActivation
from django.core.context_processors import csrf
from django.template import RequestContext
import logic, urllib, string

# Create your views here.

def searchComics(request, searchValue=None):
    pageIndex = 1
    if request.GET.get("page") != None:
        pageIndex = int(request.GET.get("page"))
            
    return searchComicsPage(request, searchValue, pageIndex)

def searchComicsPage(request, searchValue, pageIndex):
    if searchValue == None:
        searchValue = ""
                
    if request.method == "POST":                
        searchValue = urllib.quote_plus(request.POST.get("search").replace("/",""))
        destinationUrl = "/comic/search/" + searchValue        
        return HttpResponseRedirect(destinationUrl)
        
    if searchValue != "":    
        page = logic.searchComics(searchValue.strip(), pageIndex, 25)
    else:
        page = None
            
    contextData = { 'page' : page, 'searchValue' : searchValue }
    context = RequestContext(request, contextData)
    context.update(csrf(request))
    return render_to_response('comicSearch.html', context)

def resetPasswordSent(request):
    return render_to_response('resetPasswordSent.html', None)

def resetPassword(request, activationKey):
    try:
        record = UserActivation.objects.get(activationKey=activationKey)
        if not record.user.is_active:
            return HttpResponseRedirect("/comic/login/") # add a cute error redirect here for the smartass that tries this.             
    except UserActivation.DoesNotExist:
        return HttpResponseRedirect("/comic/login/")
        
    if request.method == "GET":
        form = PasswordResetForm(initial={'activationKey' : activationKey})
    else:
        form = PasswordResetForm(request.POST, initial={'activationKey' : activationKey})
        if form.is_valid():
            email = form.cleaned_data.get("email")  
            password = form.cleaned_data.get("password")          
            logic.resetPassword(email, password, activationKey)
            return HttpResponseRedirect("/comic/login/")
    
    
    contextData = { 'form' : form }
    context = RequestContext(request, contextData)
    context.update(csrf(request))
    return render_to_response('resetPassword.html', context)
            

def resetPasswordRequest(request):        
    if request.method == "GET":
        form = RequestPasswordResetForm()
    else:
        form = RequestPasswordResetForm(request.POST) 
        if form.is_valid():
            logic.initiatePasswordReset(request.POST.get("email"))
            return HttpResponseRedirect("/comic/account/reset/sent/")                    
    
    contextData = { "form" : form }        
    context = RequestContext(request, contextData)
    context.update(csrf(request))
    return render_to_response('resetPasswordRequest.html', context)  

def newComic(request):
    page = logic.getLatestComics()
    
    if request.method == "GET":
        context = RequestContext(request, { "page" : page })
        context.update(csrf(request))        
        return render_to_response('comic.html', context)
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/comic/login")
        
    form = CreateComicForm(request.POST)
    errors = None
    existingComicId = None
    existingComicUser = None
    
    if form.is_valid():
        user = request.user
        title = form.cleaned_data.get("title")
        panel1Id = form.cleaned_data.get("panel1Id")
        panel2Id = form.cleaned_data.get("panel2Id")
        panel3Id = form.cleaned_data.get("panel3Id")
        panel4Id = form.cleaned_data.get("panel4Id")
        panel5Id = form.cleaned_data.get("panel5Id")
        panel6Id = form.cleaned_data.get("panel6Id")
    
        result = logic.createComic(user, title, panel1Id, panel2Id, panel3Id, panel4Id, panel5Id, panel6Id)                
            
        if result != None and result["comicExisted"]:
            existingComicId = result['comic'].id
            existingComicUser = result['comic'].createdby.username            
        elif result != None and not result["comicExisted"]:
            return HttpResponseRedirect("/comic/" + str(result["comic"].id))            
    else:
        errors = form.errors
    
    
    context = RequestContext(request, { 
                                       "errors" : errors, 
                                       "existingComicId" : existingComicId, 
                                       "existingComicUser" : existingComicUser,
                                       "page" : page
                                       })
    context.update(csrf(request))        
    return render_to_response('comic.html', context)    
            
def viewComic(request, comicId):
    try:
        comic = Comic.objects.get(id=comicId)
    except Comic.DoesNotExist:
        return HttpResponseRedirect("/comic/")
        
    contextData = {
        'comicTitle' : comic.title,
        'comicCreator' : comic.createdby.username,
        'panel1Url' : logic.getComicUrl(comic.panel1),
        'panel2Url' : logic.getComicUrl(comic.panel2),
        'panel3Url' : logic.getComicUrl(comic.panel3),
        'panel4Url' : logic.getComicUrl(comic.panel4),
        'panel5Url' : logic.getComicUrl(comic.panel5),
        'panel6Url' : logic.getComicUrl(comic.panel6)
    }
        
    context = RequestContext(request, contextData)    
    return render_to_response('comicView.html', context)

def login(request):
    errorMessage = None
    
    if request.method == "POST":     
        errorMessage = logic.loginUser(request, request.POST.get("username"), request.POST.get("password"))
        if errorMessage == None:
            return HttpResponseRedirect("/comic/")
    
    context = RequestContext(request, { 'errorMessage' : errorMessage  })
    context.update(csrf(request))        
    return render_to_response('login.html', context)

def createAccount(request):           
    form = None
    errors = None
    activationUrl = None
    
    if request.method == "POST":
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            logic.createUser(form.cleaned_data.get("username"), form.cleaned_data.get("password"), form.cleaned_data.get("email"))
            #return HttpResponseRedirect("/comic/account/create/thanks") # for the actual "production" environment
            activationUrl = logic.getActivationUrlForUser(form.cleaned_data.get("username"))
        else:
            errors = form.errors
    else:
        form = CreateAccountForm()
    
    context = RequestContext(request, { 'form' : form, "errors" : errors, 'activationUrl' : activationUrl })    
    context.update(csrf(request))
    return render_to_response('create_account.html', context)

def logout(request):
    logic.logoutUser(request)
    return HttpResponseRedirect("/comic/login/")

def createAccountThanks(request):
    return render_to_response('thanks.html', None)

def activateAccount(request, activationKey):        
    logic.activateUser(activationKey)
    return HttpResponseRedirect("/comic/login/")

def about(request):
    return render_to_response('about.html', None)