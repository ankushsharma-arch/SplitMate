from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from django.contrib.auth.models import User

from groups.models import Group
from .models import Expense, ExpenseSplit
from .serializers import ExpenseSerializer, ExpenseSplitSerializer


# ---------------------------------------------------------------------------
# Currency helpers
# ---------------------------------------------------------------------------

EXCHANGE_RATES = {
    ('USD', 'INR'): 83.5,
    ('EUR', 'INR'): 90.2,
    ('GBP', 'INR'): 106.1,
    ('INR', 'USD'): 0.012,
    ('INR', 'EUR'): 0.011,
    ('INR', 'GBP'): 0.0094,
}


def convert(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    rate = EXCHANGE_RATES.get((from_currency, to_currency), 1.0)
    return amount * rate


# ---------------------------------------------------------------------------
# Expense creation
# ---------------------------------------------------------------------------

class ExpenseCreateView(APIView):
    permission_classes = []

    def post(self, request):
        group_id = request.data.get('group')
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)

        amount      = request.data.get('amount')
        currency    = request.data.get('currency', group.currency)
        description = request.data.get('description', '')
        notes       = request.data.get('notes', '')
        paid_by_id  = request.data.get('paid_by', request.user.id)

        try:
            paid_by = User.objects.get(pk=paid_by_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=400)

        expense = Expense.objects.create(
            group=group,
            description=description,
            amount=amount,
            currency=currency,
            paid_by=paid_by,
            notes=notes,
        )

        splits_data = request.data.get('splits')
        if splits_data:
            for s in splits_data:
                ExpenseSplit.objects.create(
                    expense=expense,
                    user_id=s['user'],
                    amount=s['amount'],
                )
        else:
            self._equal_split(expense, group, float(amount))

        return Response(ExpenseSerializer(expense).data, status=201)

    def _equal_split(self, expense, group, total):
        members = list(group.members.all())
        n       = len(members)
        share   = total // n
        for member in members:
            ExpenseSplit.objects.create(
                expense=expense,
                user=member,
                amount=share,
            )


# ---------------------------------------------------------------------------
# Expense listing & detail
# ---------------------------------------------------------------------------

class ExpenseListView(generics.ListAPIView):
    serializer_class   = ExpenseSerializer
    permission_classes = []

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return Expense.objects.filter(group_id=group_id)


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ExpenseSerializer
    permission_classes = []
    queryset           = Expense.objects.all()


# ---------------------------------------------------------------------------
# Settle-up
# ---------------------------------------------------------------------------

class SettleUpView(APIView):
    permission_classes = []

    def get(self, request, group_id):
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)

        net          = self._net_balances(group)
        transactions = self._minimise(net, group)
        return Response({'group': group.name, 'transactions': transactions})

    def _net_balances(self, group):
        from payments.models import Payment

        net = {m.id: 0.0 for m in group.members.all()}

        for exp in group.expenses.select_related('paid_by').prefetch_related('splits'):
            converted = convert(exp.amount, exp.currency, group.currency)
            net[exp.paid_by_id] = net.get(exp.paid_by_id, 0.0) + converted
            for sp in exp.splits.all():
                converted_share = convert(sp.amount, exp.currency, group.currency)
                net[sp.user_id] = net.get(sp.user_id, 0.0) - converted_share

        for p in Payment.objects.filter(group=group):
            net[p.payer_id] = net.get(p.payer_id, 0.0) + p.amount
            net[p.payee_id] = net.get(p.payee_id, 0.0) - p.amount

        return net

    def _minimise(self, net, group):
        from django.contrib.auth.models import User as DUser
        user_map = {u.id: u.username for u in DUser.objects.filter(id__in=net.keys())}

        creditors = sorted([(uid, v) for uid, v in net.items() if v > 0.01],  key=lambda x: -x[1])
        debtors   = sorted([(uid, -v) for uid, v in net.items() if v < -0.01], key=lambda x: -x[1])

        txns = []
        i = j = 0
        while i < len(creditors) and j < len(debtors):
            cid, credit = creditors[i]
            did, debt   = debtors[j]
            paid        = min(credit, debt)
            txns.append({
                'from':   user_map[did],
                'to':     user_map[cid],
                'amount': round(paid, 2),
            })
            creditors[i] = (cid, credit - paid)
            debtors[j]   = (did, debt - paid)
            if creditors[i][1] < 0.01: i += 1
            if debtors[j][1]   < 0.01: j += 1

        return txns
