# -*- coding: UTF-8 -*-
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def famfamfam_flag_icon(current_lang):
    """
    maps to famfamfam_flag css
    """
    flag_code = {
        'de': 'de',
        'en-gb': 'england',
        'en-us': 'us',
    }.get(current_lang.get('code'), 'england')

    result = '<i class="famfamfam-flag-{flag_code}"></i>'.format(flag_code=flag_code,
                                                               name=current_lang.get('name_translated'))
    return mark_safe(result)
