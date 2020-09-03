from django.db import models
from django.urls import reverse

# Create your models here.
class UserID(models.Model):
    userID = models.CharField(max_length=6)
    

    def __int__(self):
        return self.userID

    def get_absolute_url(self):
        return reverse('globalID_interface', kwargs={'pk': self.userID})