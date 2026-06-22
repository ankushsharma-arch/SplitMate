from django.db import models
from django.contrib.auth.models import User
from groups.models import Group


class Expense(models.Model):
    group        = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    description  = models.CharField(max_length=255)
    amount       = models.FloatField()
    currency     = models.CharField(max_length=3, default='INR')
    paid_by      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paid_expenses')
    created_at   = models.DateTimeField(auto_now_add=True)
    notes        = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.description} — {self.amount} {self.currency}"


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_splits')
    amount  = models.FloatField()

    class Meta:
        unique_together = ('expense', 'user')

    def __str__(self):
        return f"{self.user.username}: {self.amount}"
