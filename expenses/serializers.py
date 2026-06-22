from rest_framework import serializers
from .models import Expense, ExpenseSplit


class ExpenseSplitSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model  = ExpenseSplit
        fields = ['id', 'user', 'username', 'amount']


class ExpenseSerializer(serializers.ModelSerializer):
    splits     = ExpenseSplitSerializer(many=True, read_only=True)
    paid_by_name = serializers.CharField(source='paid_by.username', read_only=True)

    class Meta:
        model  = Expense
        fields = ['id', 'group', 'description', 'amount', 'currency',
                  'paid_by', 'paid_by_name', 'notes', 'created_at', 'splits']
