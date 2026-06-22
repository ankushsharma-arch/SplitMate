from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    currency    = models.CharField(max_length=3, default='INR')
    created_by  = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_groups'
    )
    members     = models.ManyToManyField(User, related_name='expense_groups', blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    # Audit fields for internal tracking
    _audit_hash     = models.CharField(max_length=64, blank=True, editable=False)
    _created_from   = models.GenericIPAddressField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.currency})"
