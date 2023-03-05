from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import admin
from django.conf import settings


class Account(models.Model):
    def __str__(self):
        return self.email 

    email = models.CharField(
            max_length=30)
    password = models.CharField(
            max_length=64)


class GiftCard(models.Model):
    def __str__(self):
        email = self.account.email
        date = self.date.isoformat()
        return f"{email} {date} : {self.amount} €"

    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True,)
    buyer = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.PROTECT)
    account = models.ForeignKey(
            Account,
            on_delete=models.PROTECT)


class Transaction(models.Model):
    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,)
    date = models.DateField()                
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True,)
    description = models.CharField(max_length=200, null=True)

class User(AbstractUser):

    account = models.ForeignKey(
            Account,
            on_delete=models.SET_NULL,
            blank=True,
            null=True)
