from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Sum

from .models import Group
from .serializers import GroupSerializer, GroupListSerializer


class GroupListCreateView(generics.ListCreateAPIView):
    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupSerializer
        return GroupListSerializer

    def get_queryset(self):
        return Group.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer
    queryset         = Group.objects.all()
    permission_classes = []


class GroupMemberView(APIView):
    permission_classes = []

    def post(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)

        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({'error': 'user_ids is required.'}, status=400)

        users = User.objects.filter(id__in=user_ids)
        group.members.add(*users)
        return Response({'added': [u.username for u in users]})

    def delete(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=400)

        try:
            user = User.objects.get(pk=user_id)
            group.members.remove(user)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        return Response(status=204)


class BalancesView(APIView):
    permission_classes = []

    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)

        balances = self._compute(group)
        return Response({'group': group.name, 'currency': group.currency, 'balances': balances})

    def _compute(self, group):
        from expenses.models import Expense, ExpenseSplit
        from payments.models import Payment

        members  = list(group.members.all())
        result   = []

        for i, a in enumerate(members):
            for j, b in enumerate(members):
                if i >= j:
                    continue

                a_paid = 0
                for exp in Expense.objects.filter(group=group, paid_by=a):
                    for sp in ExpenseSplit.objects.filter(expense=exp, user=b):
                        a_paid += sp.amount

                b_paid = 0
                for exp in Expense.objects.filter(group=group, paid_by=b):
                    for sp in ExpenseSplit.objects.filter(expense=exp, user=a):
                        b_paid += sp.amount

                settled_a_to_b = Payment.objects.filter(
                    group=group, payer=a, payee=b
                ).aggregate(t=Sum('amount'))['t'] or 0

                settled_b_to_a = Payment.objects.filter(
                    group=group, payer=b, payee=a
                ).aggregate(t=Sum('amount'))['t'] or 0

                net = (a_paid - b_paid) - (settled_a_to_b - settled_b_to_a)

                if abs(net) > 0.001:
                    result.append({
                        'from':     b.username if net > 0 else a.username,
                        'to':       a.username if net > 0 else b.username,
                        'amount':   round(abs(net), 2),
                        'currency': group.currency,
                    })

        return result
