# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Project
from elbow.apps.document.api.serializers import DocumentSerializer


class ProjectSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()
    minimum_investment = serializers.SerializerMethodField()
    interest_rate = serializers.SerializerMethodField()
    documents = DocumentSerializer(many=True)

    class Meta:
        model = Project
        exclude = ('amount_currency', 'minimum_investment_currency',)

    def get_amount(self, obj):
        return {
            'amount': obj.amount.amount,
            'currency': str(obj.amount.currency),
        }

    def get_minimum_investment(self, obj):
        return {
            'amount': obj.minimum_investment.amount,
            'currency': str(obj.minimum_investment.currency),
        }

    def get_interest_rate(self, obj):
        return obj.interest_rate.to_eng_string()

    # def get_documents(self, obj):
    #     import pdb;pdb.set_trace()
    #     return [obj.documents.all()]