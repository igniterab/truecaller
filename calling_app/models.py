from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=50, null=True)
    phone_no = models.IntegerField(null=False)
    is_spam = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=50, null=True)
    phone_no = models.IntegerField(null=False, unique=True)
    is_spam = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name) + "-" + str(self.user)


# Here the relationship aka Mapping is done
class CompleteDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
