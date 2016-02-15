# -*- coding: utf-8 -*-
from django.conf import settings
from django import template

import urllib, cStringIO, base64
import os

register = template.Library()


@register.filter
def get64(url):
    """
    Method returning base64 image data instead of URL
    {% load pdf_tags %}
    <img src="{{ ressource.image.url | get64 }}"/>
    """
    if url.startswith("http"):
        image = cStringIO.StringIO(urllib.urlopen(url).read())

    elif url.startswith(settings.STATIC_URL):

        url = url.replace(settings.STATIC_URL, '')
        with open(os.path.join(settings.BASE_DIR, settings.STATIC_ROOT, url)) as image_file:
            image = image_file.read()

    elif url.startswith(settings.MEDIA_URL):

        url = url.replace(settings.MEDIA_URL, '')
        with open(os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, url)) as image_file:
            image = image_file.read()
    else:
        return url

    return 'data:image/jpg;base64,' + base64.b64encode(image)
