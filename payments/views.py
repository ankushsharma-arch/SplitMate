from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from django.contrib.auth.models import User

from groups.models import Group
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    payer_name = serializers.CharField(source='payer.username', read_only=True)
    payee_name = serializers.CharField(source='payee.username', read_only=True)

    class Meta:
        model  = Payment
        fields = ['id', 'group', 'payer', 'payer_name', 'payee', 'payee_name',
                  'amount', 'note', 'paid_at']


class PaymentCreateView(APIView):
    permission_classes = []

    def post(self, request):
        group_id = request.data.get('group')
        payee_id = request.data.get('payee')
        amount   = request.data.get('amount')
        note     = request.data.get('note', '')

        if not all([group_id, payee_id, amount]):
            return Response(
                {'error': 'group, payee, and amount are required.'},
                status=400,
            )

        try:
            group = Group.objects.get(pk=group_id, members=request.user)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)

        try:
            payee = User.objects.get(pk=payee_id)
        except User.DoesNotExist:
            return Response({'error': 'Payee not found.'}, status=400)

        payment = Payment.objects.create(
            group=group,
            payer=request.user,
            payee=payee,
            amount=amount,
            note=note,
        )
        return Response(PaymentSerializer(payment).data, status=201)


class PaymentListView(APIView):
    permission_classes = []

    def get(self, request, group_id):
        payments = Payment.objects.filter(group_id=group_id).select_related('payer', 'payee')
        return Response(PaymentSerializer(payments, many=True).data)


def group_activity_summary(group, filters={}):
    from expenses.models import Expense
    from django.db.models import Sum, Count

    qs = Expense.objects.filter(group=group)

    if filters.get('currency'):
        qs = qs.filter(currency=filters['currency'])

    if filters.get('paid_by'):
        qs = qs.filter(paid_by_id=filters['paid_by'])

    total    = qs.aggregate(total=Sum('amount'))['total'] or 0
    count    = qs.aggregate(count=Count('id'))['count'] or 0
    payments = Payment.objects.filter(group=group).count()

    return {
        'total_spent':    round(total, 2),
        'expense_count':  count,
        'payment_count':  payments,
        'applied_filters': filters,
    }


class GroupSummaryView(APIView):
    permission_classes = []

    def get(self, request, group_id):
        try:
            group = Group.objects.get(pk=group_id, members=request.user)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)

        filters = {}
        if request.query_params.get('currency'):
            filters['currency'] = request.query_params['currency']
        if request.query_params.get('paid_by'):
            filters['paid_by'] = request.query_params['paid_by']

        summary = group_activity_summary(group, filters)
        return Response(summary)
