# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework import serializers

from ..models import Project
from moneyed.localization import format_money


class ProjectSerializer(serializers.ModelSerializer):
    urls = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    minimum = serializers.SerializerMethodField()
    num_backers = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('urls', 'amount', 'minimum', 'interest_rate', 'num_backers', 'percent', 'revenue', )
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    def _custom_money_format(self, money):
        try:
            return format_money(money).split('.')[0].replace(',', '.')
        except:
            return str(money.amount)

    def get_urls(self, obj):
        return {
            'detail': '%s%s' % (getattr(settings, 'BASE_URL', None), obj.url),
            'invest_now': '%s%s' % (getattr(settings, 'BASE_URL', None), obj.invest_now_url),
        }

    def get_amount(self, obj):
        return {
            'amount': self._custom_money_format(obj.amount),
            'currency': str(obj.amount.currency),
        }

    def get_minimum(self, obj):
        return {
            'amount': self._custom_money_format(obj.minimum_investment),
            'currency': str(obj.minimum_investment.currency),
        }

    def get_interest_rate(self, obj):
        return obj.interest_rate.to_eng_string()

    def get_num_backers(self, obj):
        return obj.num_backers

    def get_percent(self, obj):
        return round(obj.percent, 3)

    def get_revenue(self, obj):
        return {
            'amount': self._custom_money_format(obj.revenue),
            'currency': str(obj.revenue.currency)
        }

    def get_news_history(self, obj):
        return obj.news_history
