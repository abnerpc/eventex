# coding: utf-8

from django.core.urlresolvers import reverse as r
from django.test import TestCase
from .models import Subscription
from django.db import IntegrityError
from .forms import SubscriptionForm

class SubscriptionUrlTest(TestCase):
    def test_get_subscribe_page(self):
        response = self.client.get(r('subscriptions:subscribe'))
        self.assertEquals(200, response.status_code)


    def test_get_success_page(self):
        response = self.client.get(r('subscriptions:success', args=[1]))
        self.assertEquals(200, response.status_code)
        

class SubscribeViewTest(TestCase):

    def setUp(self):
        self.resp = self.client.get(r('subscriptions:subscribe'))

    def test_get(self):
        "Ao visitar /inscricao/ a página de inscrição é exibida."
        self.assertEquals(200, self.resp.status_code)

    def test_use_template(self):
        "O corpo da resposta deve conter a renderização de um template."
        self.assertTemplateUsed(self.resp, 'subscriptions/subscription_form.html')

    def test_has_form(self):
        "A resposta deve conter o formulário de inscrição"
        self.assertIsInstance(self.resp.context['form'], SubscriptionForm)

    def test_form_has_fields(self):
        "O formulário deve conter os campos: name, email, cpf e phone."
        form = self.resp.context['form']
        self.assertItemsEqual(['name', 'email', 'cpf', 'phone'], form.fields)

    def test_html(self):
        "O html deve conter os campos do formulário"
        self.assertContains(self.resp, '<form')
        self.assertContains(self.resp, '<input', 6)
        self.assertContains(self.resp, 'type="text"', 4)
        self.assertContains(self.resp, 'type="submit"')

class SubscriptionModelTest(TestCase):
    
    def test_create(self):
        "O model deve ter: name, cpf, email, phone e created_at"
        s = Subscription.objects.create(
            name = 'Abner Campanha',
            cpf = '012345678901',
            email = 'abnerpc@gmail.com',
            phone = '12-34567891'
        )
        self.assertEquals(s.id, 1)


class SubscriptionModelUniqueTest(TestCase):

    def setUp(self):
        # Cria uma primeira inscrição no banco
        Subscription.objects.create(name='Abner Campanha', cpf='012345678901',
            email='abnerpc@gmail.com', phone='12-34567891')
        
    def test_cpf_must_be_unique(self):
        'CPF deve ser único'
        # Instancia a inscrição com CPF existente
        s = Subscription(name='Abner Campanha', cpf='012345678901',
            email='outro@email.com.br', phone='12-34567891')
        # Verifica se ocorre o erro de integridade ao persistir.
        self.assertRaises(IntegrityError, s.save)

    def test_email_must_be_unique(self):
        'Email deve ser único'
        # Instancia a inscrição com Email existente
        s = Subscription(name='Abner Campanha', cpf='00000000000',
            email='abnerpc@gmail.com', phone='12-34567891')
        # Verifica se ocorre o erro de integridade ao persistir.
        self.assertRaises(IntegrityError, s.save)
        
class SubscribeViewPostTest(TestCase):
    
    def setUp(self):
        data = dict(name = 'Abner Campanha', cpf = '00000000000', email = 'abnerpc@gmail.com', phone = '12-34567890')
        self.resp = self.client.post(r('subscriptions:subscribe'), data)

    def test_redirects(self):
        "Post deve redirecionar para página de sucesso."
        self.assertRedirects(self.resp, r('subscriptions:success', args=[1]))

    def test_save(self):
        "Post deve salvar Subscription no banco."
        self.assertTrue(Subscription.objects.exists())

class SubscribeViewInvalidPostTest(TestCase):
    
    def setUp(self):
        data = dict(name = 'Abner Campanha', cpf = '000000000001', email = 'abnerpc@gmail.com', phone = '12-34567890')
        self.resp = self.client.post(r('subscriptions:subscribe'), data)

    def test_show_page(self):
        "Post inválido não deve redirecionar."
        self.assertEqual(200, self.resp.status_code)

    def test_form_errors(self):
        "Form deve conter erros."
        self.assertTrue(self.resp.context['form'].errors)

    def test_must_not_save(self):
        "Dados não devem ser salvos."
        self.assertFalse(Subscription.objects.exists())
