# coding: utf-8

from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from src.core.models import Speaker, Talk


def homepage(request):
    return direct_to_template(request, template='index.html')


def speaker_detail(request, slug):
    speaker = get_object_or_404(Speaker, slug=slug)
    return direct_to_template(
        request,
        'core/speaker_detail.html',
        {'speaker': speaker})


def talks(request):
    context = {
        'morning_talks': Talk.objects.at_morning(),
        'afternoon_talks': Talk.objects.at_afternoon(),
    }
    return direct_to_template(request, 'core/talks.html', context)


def talk_detail(request, pk):
    talk = get_object_or_404(Talk, pk=pk)
    return direct_to_template(request, 'core/talk_detail.html', {'talk': talk})


def talks_by_speaker(request, slug):
    speaker = get_object_or_404(Speaker, slug=slug)
    talks = Talk.objects.filter(speakers__in=[speaker.pk])
    return direct_to_template(request, 'core/talks_speaker.html', {'talks': talks})
