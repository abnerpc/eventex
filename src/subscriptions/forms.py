# coding: utf-8

from django import forms
from .models import Subscription
from django.utils.translation import ugettext as _
from django.contrib.localflavor.br.forms import BRCPFField
from django.core.validators import EMPTY_VALUES


class PhoneWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        attrs_1 = attrs or {}
        attrs_2 = attrs_1.copy()
        attrs_1.update({'size': '1', 'maxlength': '2'})
        attrs_2.update({'size': '10', 'maxlength': '8'})
        widgets = (
            forms.TextInput(attrs=attrs_1),
            forms.TextInput(attrs=attrs_2)
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
            forms.CharField(),
            forms.CharField(max_length=8,)
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

    name = forms.CharField(label=_('Nome'), max_length=100, widget=forms.TextInput(attrs={'size': '50'}))
    cpf = BRCPFField(label=_('CPF'), max_length=11, widget=forms.TextInput(attrs={'size': '20'}))
    email = forms.EmailField(label=_('E-mail'), required=False, widget=forms.TextInput(attrs={'size': '30'}))
    phone = PhoneField(label=_('Telefone'), required=False)

    def _unique_check(self, fieldname, error_message):
        param = {fieldname: self.cleaned_data[fieldname]}
        try:
            s = Subscription.objects.get(**param)
        except Subscription.DoesNotExist:
            return self.cleaned_data[fieldname]
        raise forms.ValidationError(error_message)

    def clean_email(self):
        return self._unique_check('email', _(u'E-mail já inscrito.'))

    def clean(self):
        super(SubscriptionForm, self).clean()

        if not self.cleaned_data.get('email') and not self.cleaned_data.get('phone'):
            raise forms.ValidationError(_(u'Informe seu e-mail ou telefone.'))

        return self.cleaned_data

    class Meta:
        model = Subscription
        exclude = ('paid',)
