# -*- coding: UTF-8 -*-
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from rest_framework import routers

from elbow.apps.project.api.views import ProjectListAPIViewset

router = routers.SimpleRouter()

router.register(r'projects', ProjectListAPIViewset)

#
# Standard URLS
#
urlpatterns = router.urls
