# coding: utf-8

from django.test import TestCase
from django.core.urlresolvers import reverse as r
from .models import Speaker, Contact, Talk, PeriodManager, Media


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


class TalkModelTest(TestCase):
    """Teste do model Talk"""
    def setUp(self):
        self.talk = Talk.objects.create(
            title=u'Introdução ao Python',
            description=u'Descrição da Palestra',
            start_time='10:00')

    def test_create(self):
        self.assertEqual(1, self.talk.pk)

    def test_unicode(self):
        self.assertEqual(u'Introdução ao Python', unicode(self.talk))

    def test_period_manager(self):
        self.assertIsInstance(Talk.objects, PeriodManager)


class PeriodManagerTest(TestCase):
    """Teste do manager"""
    def setUp(self):
        Talk.objects.create(title=u'Morning Talk', start_time='10:00')
        Talk.objects.create(title=U'Afternoon Talk', start_time='12:00')

    def test_morning(self):
        self.assertQuerysetEqual(
            Talk.objects.at_morning(),
            ['Morning Talk'],
            lambda t: t.title)

    def test_afternoon(self):
        self.assertQuerysetEqual(
            Talk.objects.at_afternoon(),
            ['Afternoon Talk'],
            lambda t: t.title)


class TalksViewTest(TestCase):
    """Teste da view de Talks"""
    def setUp(self):
        self.resp = self.client.get(r('core:talks'))

    def test_get(self):
        self.assertEqual(200, self.resp.status_code)

    def test_template(self):
        self.assertTemplateUsed(self.resp, 'core/talks.html')

    def test_morning_talks_in_context(self):
        self.assertIn('morning_talks', self.resp.context)

    def test_afternoon_talks_in_context(self):
        self.assertIn('afternoon_talks', self.resp.context)


class MediaModelTest(TestCase):
    """Teste do model Media"""
    def setUp(self):
        talk = Talk.objects.create(
            title=u'Talk 1',
            start_time='10:00')
        self.media = Media.objects.create(
            talk=talk,
            type='YT',
            media_id='QjA5faZF1A8',
            title='Video')

    def test_create(self):
        self.assertEqual(1, self.media.pk)

    def test_unicode(self):
        self.assertEqual("Talk 1 - Video", unicode(self.media))


class TalkDetailTest(TestCase):
    """Teste da view de detalhe de um talk"""
    def setUp(self):
        talk = Talk.objects.create(
            title='Talk',
            start_time='10:00'
        )
        self.media = Media.objects.create(
            talk=talk,
            type='YT',
            media_id='QjA5faZF1A8',
            title='Video')
        self.resp = self.client.get(r('core:talk_detail', args=[1]))

    def test_get(self):
        self.assertEqual(200, self.resp.status_code)

    def test_template(self):
        self.assertTemplateUsed(self.resp, 'core/talk_detail.html')

    def test_talk_in_context(self):
        talk = self.resp.context['talk']
        self.assertIsInstance(talk, Talk)
