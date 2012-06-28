# coding: utf-8

from django.core.urlresolvers import reverse as r
from django.test import TestCase
from .models import Subscription
from django.db import IntegrityError
from .forms import SubscriptionForm
from django.core import mail
from mock import Mock
from .admin import SubscriptionAdmin, Subscription, admin
from django.contrib.auth.models import User


class SubscriptionUrlTest(TestCase):

    def test_get_subscribe_page(self):
        response = self.client.get(r('subscriptions:subscribe'))
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
        self.assertContains(self.resp, '<input', 7)
        self.assertContains(self.resp, 'type="text"', 5)
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

    def test_email_sent(self):
        "Post deve notificar visitante por email."
        self.assertEquals(1, len(mail.outbox))


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


class SuccessViewTest(TestCase):

    def setUp(self):
        s = Subscription.objects.create(
            name = 'Abner Campanha',
            cpf = '00000000000',
            email = 'abnerpc@gmail.com',
            phone = '12-34567890'
        )
        self.resp = self.client.get(r('subscriptions:success', args=[s.pk]))

    def test_get(self):
        "Visita /inscricao/1/ e retorna 200."
        self.assertEquals(200, self.resp.status_code)

    def test_template(self):
        "Renderiza template."
        self.assertTemplateUsed(self.resp, 'subscriptions/subscription_detail.html')

    def test_context(self):
        "Verifica instância de subscription no contexto."
        subscription = self.resp.context['subscription']
        self.assertIsInstance(subscription, Subscription)

    def test_html(self):
        "Página deve conter nome do cadastrado."
        self.assertContains(self.resp,'Abner Campanha')


class SuccessViewNotFound(TestCase):

    def test_not_found(self):
        "Acesso à inscrição não cadastrada deve retornar 404."
        response = self.client.get(r('subscriptions:success', args=[0]))
        self.assertEquals(404, response.status_code)


class CustomActionTest(TestCase):

    def setUp(self):
        Subscription.objects.create(
            name='Abner Campanha',
            cpf='01234567890',
            email='abnerpc@gmail.com',
            phone='12-34567890'
        )
        self.modeladmin = SubscriptionAdmin(Subscription, admin.site)
        # action!
        self.modeladmin.mark_as_paid(Mock(), Subscription.objects.all())

    def test_update(self):
        'Os dados devem ser atualizados como pago de acordo com o Queryset.'
        self.assertEqual(1, Subscription.objects.filter(paid=True).count())


class ExportSubscriptionViewTest(TestCase):

    def setUp(self):
        User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
        assert self.client.login(username='admin', password='admin')
        self.resp = self.client.get(r('admin:export_subscriptions'))

    def test_get(self):
        u'Sucesso ao acessar url de download do arquivo csv.'
        self.assertEqual(200, self.resp.status_code)

    def test_content_type(self):
        u'Content type deve ser text/csv.'
        self.assertEqual('text/csv', self.resp['Content-Type'])

    def test_attachment(self):
        u'Header indicando ao browser que a resposta é um arquivo a ser salvo'
        self.assertTrue('attachment;' in self.resp['Content-Disposition'])


class ExportSubscriptionsNotFound(TestCase):

    def test_404(self):
        u'Login é exigido para download do csv'
        '''
        Quando o usuário não está autenticado
        o admin responde 200 e renderiza o html de login 
        '''
        response = self.client.get(r('admin:export_subscriptions'))
        self.assertTemplateUsed(response, 'admin/login.html')


class SubscriptionFormTest(TestCase):

    def test_cpf_has_only_digits(self):
        u'CPF deve ter apenas dígitos.'
        form = self.make_and_validade_form(cpf='0000000000a')
        self.assertDictEqual(form.errors, {'cpf': [u'Este campo requer somente números.']})

    def test_cpf_has_11_digits(self):
        u'CPF deve ter 11 dígitos.'
        form = self.make_and_validade_form(cpf='000000000012')
        self.assertDictEqual(form.errors,
            {'cpf': [u'Certifique-se de que o valor tenha no máximo 11 caracteres (ele possui 12).']}
        )

    def test_must_inform_email_or_phone(self):
        u'Email e Phone são opcionais, mas ao menos 1 precisa ser informado.'
        form = self.make_and_validade_form(email='', phone='')
        self.assertDictEqual(form.errors, {'__all__': [u'Informe seu e-mail ou telefone.']})

    def make_and_validade_form(self, **kwargs):
        data = dict(
            name='Abner Campanha',
            email='abnerpc@gmail.com',
            cpf='00000000000',
            phone='12-34567890'
        )
        data.update(kwargs)
        form = SubscriptionForm(data)
        form.is_valid()
        return form
