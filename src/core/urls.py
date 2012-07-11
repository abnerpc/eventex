# coding: utf-8

from django.conf.urls import patterns, url

urlpatterns = patterns('src.core.views',
    url(
        r'^palestrantes/(?P<slug>[\w-]+)/$',
        'speaker_detail',
        name='speaker_detail'
        ),
    url(r'^palestras/$', 'talks', name='talks'),
    url(r'^palestras/(\d+)/$', 'talk_detail', name='talk_detail'),
    url(r'^palestras/speaker/(?P<slug>[\w-]+)/$', 'talks_by_speaker', name='talks_by_speaker'),
    )
