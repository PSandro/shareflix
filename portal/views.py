from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Account

def index(request):
    if request.user.is_authenticated:
        return redirect(portal)
    return redirect('login')

@login_required
def portal(request):

    user = request.user
    account = user.account
    transactions = user.transaction_set.order_by('-date')
    open_sum = transactions.aggregate(open_sum=Sum('amount'))['open_sum']
    giftcards = account.giftcard_set.order_by('-date') if account else None

    context = {
            'account': user.account,
            'transactions': transactions,
            'open_sum': open_sum,
            'giftcards': giftcards
            }

    return render(request, 'portal.html', context=context)
