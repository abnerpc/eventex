# coding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from .forms import SubscriptionForm
from django.core.urlresolvers import reverse as r
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Subscription

def subscribe(request):
    if request.method == 'POST':
        return create(request)
    else:
        return new(request)

def new(request):
    return direct_to_template(request, 'subscriptions/subscription_form.html', {'form': SubscriptionForm()})

def create(request):
    form = SubscriptionForm(request.POST)

    if not form.is_valid():
        return direct_to_template(request, 'subscriptions/subscription_form.html', {'form': form})

    subscription = form.save()
    
    #envia o email
    send_mail(
        subject=u'Cadastrado com Sucesso',
        message=u'Obrigado pela sua inscrição!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscription.email]
        )

    return HttpResponseRedirect(r('subscriptions:success', args=[subscription.pk]))

def success(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk)
    return direct_to_template(request, 'subscriptions/subscription_detail.html', {'subscription': subscription})
