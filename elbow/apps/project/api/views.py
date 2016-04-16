# -*- coding: UTF-8 -*-
from rest_framework import generics

from ..models import Project
from .serializers import (ProjectSerializer,)


class ProjectListAPIView(generics.ListAPIView):
    model = Project
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
