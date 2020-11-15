from django.db.models import Sum
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Currency(models.TextChoices):
    EUR = 'EUR', _('Euro')
    TL = 'TL', _('Lyra')

class NetflixAccount(models.Model):
    def __str__(self):
        return self.email 

    monthly_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True,)
    currency = models.CharField(
            max_length=3,
            choices=Currency.choices,
            default=Currency.TL)
    email = models.CharField(
            max_length=30)
    password = models.CharField(
            max_length=64)
    pin = models.DecimalField(max_digits=4, decimal_places=0)
    active = models.BooleanField()
    billing_date = models.DateField()

class NetflixGiftCard(models.Model):
    def __str__(self):
        return self.redemption_date 

    redemption_date = models.DateField()
    currency = models.CharField(
            max_length=3,
            choices=Currency.choices,
            default=Currency.TL)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True,)
    account = models.ForeignKey(
            NetflixAccount,
            on_delete=models.PROTECT)
class FinancialClaim(models.Model):
    def __str__(self):
        return self.user.username + ": " + str(self.beginning) + " - " + str(self.ending)

    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,)
    beginning = models.DateField()                
    ending = models.DateField(null=True,)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True,)
    class Status(models.TextChoices):
        ONGOING = 'OG', _('ongoing')
        OPEN = 'OP', _('open')
        PAID = 'PD', _('paid')
    status = models.CharField(
            max_length=2,
            choices=Status.choices,
            default=Status.ONGOING,)
    account = models.ForeignKey(
            NetflixAccount,
            on_delete=models.PROTECT)

class User(AbstractUser):
    account = models.ForeignKey(
            NetflixAccount,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,)
    def get_claims_by_status(self, status: FinancialClaim.Status):
       return self.financialclaim_set.filter(status=status) 
    def get_total_open_amount(self):
       return self.get_claims_by_status(FinancialClaim.Status.OPEN).aggregate(Sum('amount'))['amount__sum']
