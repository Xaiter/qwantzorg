from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
 
class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None


class Comic(models.Model):
    title = models.CharField(max_length=128)
    panel1 = models.IntegerField()
    panel2 = models.IntegerField()
    panel3 = models.IntegerField()
    panel4 = models.IntegerField()
    panel5 = models.IntegerField()
    panel6 = models.IntegerField()
    datecreated = models.DateTimeField()
    createdby = models.ForeignKey(User)
    
class Vote(models.Model):
    user = models.ForeignKey(User)
    comic = models.ForeignKey(Comic)
    rating = models.IntegerField()
    
class Comment(models.Model):
    user = models.ForeignKey(User)
    comic = models.ForeignKey(Comic)
    text = models.TextField()
    
class UserActivation(models.Model):
    user = models.ForeignKey(User)
    activationKey = models.CharField(max_length=128)
    keyExpires = models.DateTimeField()