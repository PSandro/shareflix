from django.db.models import Sum
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class NetflixAccount(models.Model):
    def __str__(self):
        return self.email

    email = models.CharField(
        max_length=30)
    password = models.CharField(
        max_length=64)
    pin = models.DecimalField(max_digits=4, decimal_places=0)
    active = models.BooleanField()


class NetflixGiftCard(models.Model):
    def __str__(self):
        return self.redemption_date

    redemption_date = models.DateField()
    redem_worth_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True,)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True,)
    account = models.ForeignKey(
        NetflixAccount,
        on_delete=models.PROTECT)


class FinancialClaim(models.Model):
    def __str__(self):
        return self.user.username
        + ": " + str(self.beginning)
        + " - " + str(self.ending)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,)
    beginning = models.DateField()
    ending = models.DateField(null=True,)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True,)

    class Status(models.TextChoices):
        OPEN = 'OP', _('open')
        PAID = 'PD', _('paid')

    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.OPEN,)
    account = models.ForeignKey(
        NetflixAccount,
        on_delete=models.PROTECT)

    class Meta:
        permissions = (
            ("can_add_financial_claim", "Can add cost price"),
        )


class User(AbstractUser):
    account = models.ForeignKey(
        NetflixAccount,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,)

    def get_claims_by_status(self, status: FinancialClaim.Status):
        return self.financialclaim_set.filter(status=status)

    def get_total_open_amount(self):
        return self.get_claims_by_status(
                FinancialClaim.Status.OPEN
                ).aggregate(
                        Sum('amount'))['amount__sum']
