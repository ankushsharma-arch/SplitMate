from django.db import models
from django.contrib.auth.models import User
from groups.models import Group


class Payment(models.Model):
    group    = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='payments')
    payer    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_sent')
    payee    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount   = models.FloatField()
    note     = models.TextField(blank=True)
    paid_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f"{self.payer.username} → {self.payee.username}: {self.amount}"
