# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Project
from elbow.apps.document.api.serializers import DocumentSerializer


class ProjectSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()
    minimum_investment = serializers.SerializerMethodField()
    interest_rate = serializers.SerializerMethodField()
    documents = DocumentSerializer(many=True)
    num_backers = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    news_history = serializers.SerializerMethodField()

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

    def get_num_backers(self, obj):
        return obj.num_backers

    def get_percent(self, obj):
        return obj.percent

    def get_revenue(self, obj):
        return {
            'amount': obj.revenue.amount,
            'currency': str(obj.revenue.currency)
        }

    def get_news_history(self, obj):
        return obj.news_history
