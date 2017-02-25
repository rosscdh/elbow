# -*- coding: UTF-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.authentication import SessionAuthentication

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from ..models import Project
from .serializers import (ProjectSerializer,)

from urlparse import urljoin


class ProjectListAPIViewset(ReadOnlyModelViewSet):
    model = Project
    serializer_class = ProjectSerializer
    queryset = Project.objects.public()
    lookup_field = 'slug'


class ListMenuItems(APIView):
    """
    View to list menu items depending on if user is logged in or not
    """
    authentication_classes = (SessionAuthentication,)

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        menu_items = []

        if request.user.is_authenticated():
            menu_items = [
                {
                    'name': _('Logout'),
                    'url': urljoin(settings.BASE_URL, reverse('account_logout')),
                },
                {
                    'name': _('Change Password'),
                    'url': urljoin(settings.BASE_URL, reverse('account_change_password')),
                },
            ]
        else:
            menu_items = [
                {
                    'name': _('Login'),
                    'url': urljoin(settings.BASE_URL, reverse('account_login')),
                },
                {
                    'name': _('Register'),
                    'url': urljoin(settings.BASE_URL, reverse('account_signup')),
                }
            ]

        return Response(menu_items)
