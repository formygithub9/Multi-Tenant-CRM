from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    customers = serializers.DictField()
    contacts = serializers.DictField()
    leads = serializers.DictField()
    deals = serializers.DictField()
    quotes = serializers.DictField()
    orders = serializers.DictField()
    invoices = serializers.DictField()
    payments = serializers.DictField()
    activities = serializers.DictField()