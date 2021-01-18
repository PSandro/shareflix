"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from .forms import LoginForm, ChargeForm, ProfileChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import loader
from django import template
from shareflix import billing
from datetime import datetime


@login_required(login_url="/login/")
def index(request):
    return render(request, "index.html")


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('error-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('error-500.html')
        return HttpResponse(html_template.render(context, request))


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


@login_required(login_url="/login/")
def profile_change_view(request):
    form = ProfileChangeForm(request.POST or None, instance=request.user)

    msg = None

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return render(request, "profile.html", {"form": form, "msg": msg})
        else:
            msg = 'Error validating the form'

    return render(request, "profile.html", {"form": form, "msg": msg})


@login_required(login_url="/login/")
def financial_claims_view(request):
    claims = request.user.financialclaim_set.all().order_by('-beginning')
    statistic = {
            'open': request.user.get_claims_by_status('OP').count,
            'paid': request.user.get_claims_by_status('PD').count,
            'total': request.user.get_total_open_amount(),
            }
    return render(request, "financial_claims.html",
                  {"claims": claims, "statistic": statistic})


@login_required(login_url="/login/")
def netflix_account_view(request):
    account = request.user.account

    return render(request, "netflix_account.html", {"account": account, })


@login_required(login_url="/login/")
def charge_view(request):
    form = ChargeForm(request.POST or None)

    msg = None

    if request.method == "POST":
        if form.is_valid():
            msg = "lol"
            user = form.cleaned_data['account']
            billing.charge_user(user,
                                datetime.now(),
                                datetime.now(),
                                user.account,
                                form.cleaned_data['amount'])
            return render(request, "charge.html", {"form": form, "msg": msg})
        else:
            msg = 'Error validating the form'

    return render(request, "charge.html", {"form": form, "msg": msg})
