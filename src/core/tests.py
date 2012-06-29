# coding: utf-8

from django.test import TestCase
from django.core.urlresolvers import reverse as r
from .models import Speaker, Contact


class HomepageTest(TestCase):

    def test_get_homepage(self):
        response = self.client.get('/')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'index.html')


class SpeakerModelTest(TestCase):

    def setUp(self):
        self.speaker = Speaker(
            name="Abner Campanha",
            slug="abner-campanha",
            url="http://abnerpc.com",
            description="Python/Django developer!",
            avatar="")
        self.speaker.save()

    def test_create(self):
        self.assertEqual(1, self.speaker.pk)

    def test_unicode(self):
        self.assertEqual(u"Abner Campanha", unicode(self.speaker))


class SpeakerDetailTest(TestCase):
    """Testa detalhe dos Speakers"""
    def setUp(self):
        Speaker.objects.create(
            name="Abner Campanha",
            slug="abner-campanha",
            url="http://abnerpc.com",
            description="Python developer!",
            avatar="")
        self.resp = self.client.get(
            r(
                'core:speaker_detail',
                kwargs={'slug': 'abner-campanha'}
                )
            )

    def test_get(self):
        self.assertEqual(200, self.resp.status_code)

    def test_template(self):
        self.assertTemplateUsed(self.resp, 'core/speaker_detail.html')

    def test_speaker_in_context(self):
        speaker = self.resp.context['speaker']
        self.assertIsInstance(speaker, Speaker)


class ContactModelTest(TestCase):
    """Teste do model de contato"""
    def setUp(self):
        self.speaker = Speaker.objects.create(
            name="Abner Campanha",
            slug="abner-campanha",
            url="http://abnerpc.com",
            avatar="",
            description="Python developer!")

    def test_create_email(self):
        contact = Contact.objects.create(
            speaker=self.speaker,
            kind='E',
            value='abnerpc@gmail.com')
        self.assertEqual(1, contact.pk)

    def test_create_phone(self):
        contact = Contact.objects.create(
            speaker=self.speaker,
            kind='P',
            value='12-34567890')
        self.assertEqual(1, contact.pk)

    def test_create_fax(self):
        contact = Contact.objects.create(
            speaker=self.speaker,
            kind='F',
            value='12-34567890')
        self.assertEqual(1, contact.pk)
