from shareflix.models import FinancialClaim, User, NetflixAccount
import datetime


def charge_user(user: User,
                beginning: datetime,
                ending: datetime,
                account: NetflixAccount,
                amount: float = 0.):
    if user is None:
        return
    if account is None:
        account = user.account
    if ending is None:
        today = datetime.today()
        ending = datetime(today.year, today.month, account.billing_date.day)
    if beginning is None or beginning > ending:
        beginning = ending

    FinancialClaim.objects.create(user=user,
                                  beginning=beginning,
                                  ending=ending,
                                  amount=amount,
                                  account=account,
                                  status=FinancialClaim.Status.OPEN)

# TODO: send email
