# coding: utf-8
from django import forms
from .models import Subscription
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.db.models.base import Empty

def CpfValidator(value):
    if not value.isdigit():
        raise ValidationError(_(u'O CPF deve conter apenas números'))
    if len(value) != 11:
        raise ValidationError(_(u'O CPF deve ter 11 dígitos'))

class PhoneWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs)
        )
        super(PhoneWidget, self).__init__(widgets, attrs)
        
    def decompress(self, value):
        if not value:
            return [None, None]
        return value.split('-')
        
class PhoneField(forms.MultiValueField):
    widget = PhoneWidget
    
    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(),
            forms.IntegerField()
        )
        super(PhoneField, self).__init__(fields, *args, **kwargs)
        
    def compress(self, data_list):
        if not data_list:
            return ''
        if data_list[0] in EMPTY_VALUES:
            raise forms.ValidationError(u'DDD inválido')
        if data_list[1] in EMPTY_VALUES:
            raise forms.ValidationError(u'Número inválido')
        return '%s-%s' % tuple(data_list)
            
class SubscriptionForm(forms.ModelForm):
    
    name = forms.CharField(label=_('Nome'), max_length=100)
    cpf = forms.CharField(label=_('CPF'), validators=[CpfValidator])
    email = forms.CharField(label=_('E-mail'), required=False)
    phone = PhoneField(label=_('Telefone'), required=False)
    
    def _unique_check(self, fieldname, error_message):
        param = { fieldname: self.cleaned_data[fieldname] }
        try:
            s = Subscription.objects.get(**param)
        except Subscription.DoesNotExist:
            return self.cleaned_data[fieldname]
        raise forms.ValidationError(error_message)
    
    def clean_cpf(self):
        return self._unique_check('cpf', _(u'CPF já inscrito.'))
    
    def clean_email(self):
        return self._unique_check('email', _(u'E-mail já inscrito.'))
         
    def clean(self):
        super(SubscriptionForm, self).clean()
        
        if not self.cleaned_data.get('email') and not self.cleaned_data.get('phone'):
            raise forms.ValidationError(_(u'Informe seu e-mail ou telefone'))
       
        return self.cleaned_data
        
    class Meta:
        model = Subscription
        exclude = ('paid',)
    