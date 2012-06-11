# coding: utf-8
from django import forms
from .models import Subscription

class SubscriptionForm(forms.ModelForm):
    
    class Meta:
        model = Subscription
        exclude = ('paid',)

