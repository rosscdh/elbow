# -*- coding: utf-8 -*-
from django.conf import settings
from django.apps import apps
from django.test.runner import DiscoverRunner as DjangoTestSuiteRunner


class AppTestRunner(DjangoTestSuiteRunner):
    """
    Custom Test runner so we test only our apps
    """
    def build_suite(self, test_labels, *args, **kwargs):
        # not args passed in
        if not test_labels:
            test_labels = []
            # Remove path info and use only the app "label"
            for app_name in settings.PROJECT_APPS:
                test_labels.append(app_name)
            test_labels = tuple(test_labels)

        return super(AppTestRunner, self).build_suite(test_labels, *args, **kwargs)

    def setup_test_environment(self, *args, **kwargs):
        """
        # Change all unmanaged models to use the default database for testing
        """
        self.unmanaged_models = [m for m in apps.get_models()
                                 if not m._meta.managed]

        for m in self.unmanaged_models:
            m._meta.managed = True
            m.objects.__class__._db_original = m.objects.__class__._db
            m.objects.__class__._db = 'default'

        super(AppTestRunner, self).setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        # reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False
            m.objects.__class__._db = m.objects.__class__._db_original
        super(AppTestRunner, self).teardown_test_environment(*args, **kwargs)
