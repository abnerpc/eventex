# coding: utf-8

from django.views.generic.simple import direct_to_template


def homepage(request):

    return direct_to_template(request, template='index.html')
