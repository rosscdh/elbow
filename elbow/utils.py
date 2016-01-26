# -*- coding: UTF-8 -*-
from django.conf import settings
from django.template import loader
from django.core.files.storage import FileSystemStorage

from storages.backends.s3boto import S3BotoStorage
from inmemorystorage import InMemoryStorage

from collections import namedtuple, OrderedDict


def get_namedtuple_choices(name, choices_tuple):
    """Factory function for quickly making a namedtuple suitable for use in a
    Django model as a choices attribute on a field. It will preserve order.

    Usage::

        class MyModel(models.Model):
            COLORS = get_namedtuple_choices('COLORS', (
                (0, 'black', 'Black'),
                (1, 'white', 'White'),
            ))
            colors = models.PositiveIntegerField(choices=COLORS)

        >>> MyModel.COLORS.black
        0
        >>> MyModel.COLORS.get_choices()
        [(0, 'Black'), (1, 'White')]

        class OtherModel(models.Model):
            GRADES = get_namedtuple_choices('GRADES', (
                ('FR', 'fr', 'Freshman'),
                ('SR', 'sr', 'Senior'),
            ))
            grade = models.CharField(max_length=2, choices=GRADES)

        >>> OtherModel.GRADES.fr
        'FR'
        >>> OtherModel.GRADES.get_choices()
        [('fr', 'Freshman'), ('sr', 'Senior')]

    """
    class Choices(namedtuple(name, [name for val, name, desc in choices_tuple])):
        __slots__ = ()
        _choices = tuple([desc for val, name, desc in choices_tuple])

        def get_choices(self):
            return zip(tuple(self), self._choices)

        def get_choices_dict(self):
            """
            Return an ordered dict of key and their values
            must be ordered correctly as there are items that depend on the key
            order
            """
            choices = OrderedDict()
            for k, v in self.get_choices():
                choices[k] = v
            return choices

        def get_all(self):
            for val, name, desc in choices_tuple:
                yield val, name, desc

        def get_values(self):
            values = []
            for val, name, desc in choices_tuple:
                if isinstance(val, type([])):
                    values.extend(val)
                else:
                    values.append(val)
            return values

        def get_value_by_name(self, input_name):
            for val, name, desc in choices_tuple:
                if name == input_name:
                    return val
            return False

        def get_desc_by_value(self, input_value):
            for val, name, desc in choices_tuple:
                if val == input_value:
                    return desc
            return False

        def get_name_by_value(self, input_value):
            for val, name, desc in choices_tuple:
                if val == input_value:
                    return name
            return False

        def is_valid(self, selection):
            for val, name, desc in choices_tuple:
                if val == selection or name == selection or desc == selection:
                    return True
            return False

    return Choices._make([val for val, name, desc in choices_tuple])


def CustomManagedStorage():
    """
    DEV - upload to localFS
    TEST - Overwrite local storage
    STAGING/PROD - s3BotoStorage
    """
    if settings.PROJECT_ENVIRONMENT in ['dev', 'development']:
        return FileSystemStorage()

    if settings.PROJECT_ENVIRONMENT in ['test']:
        # return OverwriteStorage()
        return InMemoryStorage()

    else:
        #return S3BotoStorage()
        return FileSystemStorage()


class HTML2TextEmailMessageService(object):
    def __init__(self, template_name, **kwargs):
        self.html = None
        self.plain_text = None
        self.template_name = template_name
        self.context = kwargs
        self.process(context=self.context)

    def process(self, context):
        """
        Render HTML template and convert into a markdown version as well
        """
        self.html = loader.render_to_string(self.template_name,
                                            context)
        self.plain_text = None  # Add html2text here so we get mardown
        # Return tuple
        return (self.plain_text, self.html)
