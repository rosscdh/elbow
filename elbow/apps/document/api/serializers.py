# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Document


class DocumentSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()

    class Meta:
        model = Document

    def get_document(self, obj):
        if obj.document:
            return obj.document.url if self.context['request'].user.is_authenticated() is True else None
        return None#obj.document.url