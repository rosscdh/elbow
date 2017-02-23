# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ReadOnlyModelViewSet
from ..models import Project
from .serializers import (ProjectSerializer,)


class ProjectListAPIViewset(ReadOnlyModelViewSet):
    model = Project
    serializer_class = ProjectSerializer
    queryset = Project.objects.public()
