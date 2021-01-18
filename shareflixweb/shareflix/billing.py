from shareflix.models import FinancialClaim, User, NetflixAccount, Currency
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

def charge_account(
                beginning: datetime,
                ending: datetime,
                account: NetflixAccount,
                amount: float = 0.):
    
    if ending is None:
        today = datetime.today()
        ending = datetime(today.year, today.month, account.billing_date.day)
    if beginning is None or beginning > ending:
        beginning = ending


    worth = subtract_amount_and_get_worth(account, amount)

    worth_part = worth / account.user_set.all().count

    for user in account.user_set.all():
        charge_user(user,
                    beginning,
                    ending,
                    account,
                    worth_part)



def substract_amount_and_get_worth(account: NetflixAccount, amount: float = 0., currency: Currency=Currency.TL):
    available_cards = account.netflixgiftcard_set.filter(
                                                        currency__exact=currency).filter(current_amount__gt=0.).order_by('-redemption_date')
    rest_amount = amount
    worth = 0.

    for card in available_cards:
        if (rest_amount > card.current_amount):
            rest_amount -= card.current_amount
            
            worth += card.current_amount * card.worth_rate

            card.current_amount = 0.
            card.save()
        else:
            card.current_amount-= rest_amount

            worth += rest_amount * card.worth_rate
            card.save()
            break

    # TODO: exception if rest_amount is not 0.

    return worth
