import datetime, random, sha, smtplib, httplib, array
from django.contrib.auth.models import User
from comics.models import UserActivation, Comic
from email.mime.text import MIMEText
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, InvalidPage, EmptyPage

def getLatestComics():
    comics = Comic.objects.all().order_by('datecreated').reverse()[:10]
    paginator = Paginator(comics, 10)
    
    try:
        page = paginator.page(1)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    
    return page
    
def searchComics(searchValue, pageIndex, pageSize):
    if pageIndex <= 0:
        pageIndex = 1
    
    comics = Comic.objects.filter(title__icontains=searchValue).order_by('datecreated').reverse()
    paginator = Paginator(comics, pageSize)
    
    try:
        page = paginator.page(pageIndex)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    
    return page    

def resetPassword(email, password, activationKey):
    record = UserActivation.objects.get(activationKey=activationKey)    
    user = User.objects.get(email=email)
    
    if record.user.id != user.id:
        raise Exception("activationKey does not belong to given user!")
        
    user.set_password(password)
    user.save()
    record.delete()
        

def initiatePasswordReset(email):
    user = User.objects.get(email=email)
    
    try:
        record = UserActivation.objects.get(user=user)
    except UserActivation.DoesNotExist:
        record = createUserActivationRecord(user)
    
    emailSubject = "qwantz.org Password Reset"
    emailBody = "Oh, hi!  You should probably click the following link to reset your password.  If you didn't request this password reset, ignore it.  Someone's just trying to annoy you.  If you did, then by all means, click it! It will expire in one day!\n\n http://momo/comic/account/reset/" + record.activationKey 

    #I am dumb and cannot get email to work locally, so pffft.  I'll just disable this for now.
    #sendEmail(emailSubject, emailBody, user.email, 'xaiter@qwantz.org')
    

def createComic(user, title, panel1Id, panel2Id, panel3Id, panel4Id, panel5Id, panel6Id):
    try:
        comic = Comic.objects.get(panel1=panel1Id, panel2=panel2Id, panel3=panel3Id, panel4=panel4Id, panel5=panel5Id, panel6=panel6Id)
        return { 'comicExisted' : True, 'comic' : comic }
    except Comic.DoesNotExist:
        if not verifyComicPanelIds([panel1Id, panel2Id, panel3Id, panel4Id, panel5Id, panel6Id]):            
            return None
               
        comic = Comic(panel1=panel1Id, panel2=panel2Id, panel3=panel3Id, panel4=panel4Id, panel5=panel5Id, panel6=panel6Id, title=title, createdby=user, datecreated=datetime.datetime.now())
        comic.save()
        return { 'comicExisted' : False, 'comic' : comic }

def createUser(username, password, email):
    try:
        user = User.objects.get(username__exact=username)
        raise Exception("User already exists!")
    except User.DoesNotExist:
        user = None        
    
    user = User.objects.create_user(username, email, password)
    user.is_active = False
    user.save()
    
    activationRecord = createUserActivationRecord(user)
    
    emailSubject = "qwantz.org Account Confirmation"
    emailBody = "Oh, hi!  You should probably click the following link to activate your account.  It will expire in one day, releasing the username and password for use again.\n\n http://momo/comic/account/activate/%s"

    #I am dumb and cannot get email to work locally, so pffft.  I'll just disable this for now.
    #sendEmail(emailSubject, emailBody, user.email, 'xaiter@qwantz.org')    

def createUserActivationRecord(user):
    salt = sha.new(str(random.random())).hexdigest()[:5]
    activationKey = sha.new(salt+user.username).hexdigest()
    keyExpires = datetime.datetime.today() + datetime.timedelta(days=1)
        
    activationRecord = UserActivation.objects.create(user=user, activationKey=activationKey, keyExpires=keyExpires)    
    activationRecord.save()
    return activationRecord

def activateUser(activationKey):
    try:
        activationRecord = UserActivation.objects.get(activationKey=activationKey)
        activationRecord.user.is_active = True
        activationRecord.user.save()
        activationRecord.delete()
    except UserActivation.DoesNotExist:
        return False
    
    return True

def loginUser(request,username, password):
    if username == None or password == None:
        return "Username and password are required."
    
    user = authenticate(username=username, password=password)
    
    if user == None:
        return "Invalid username or password."

    if not user.is_active:
        return "Your account has not been activated yet.  Contact xaiter@qwantz.org if you aren't getting an activation email."
    else:
        login(request, user)
    
    return None

def logoutUser(request):    
    logout(request)

def getActivationUrlForUser(username):    
    try:
        user = User.objects.get(username__iexact=username)
        record = UserActivation.objects.get(user=user)
    except User.DoesNotExist:
        return None
                
    return "http://momo/comic/account/activate/%s" % (record.activationKey)

def verifyComicPanelIds(panelIds):    
    for panelId in panelIds:
        if not verifyComicPanelId(panelId):
            return False
        
    return True

def getComicUrl(panelId):
    return "http://www.qwantz.com/comics/comic2-" + str(panelId) + ".png"

def verifyComicPanelId(panelId):    
    connection = httplib.HTTPConnection("qwantz.com")
    connection.request('HEAD', "/comics/comic2-" + str(panelId) + ".png")
    response = connection.getresponse()
    connection.close()
    
    return response.status == 200    
    
def sendEmail(emailSubject, emailBody, emailTo, emailFrom):
    msg = MIMEText(emailBody)
    msg['Subject'] = emailSubject
    msg['From'] = emailFrom
    msg['To'] = emailTo
    
    smtpServer = smtplib.SMTP('momo')
    smtpServer.sendmail(emailFrom, emailTo, msg.as_string())
    