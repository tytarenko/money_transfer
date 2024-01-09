from django.db import models

from django.db import models
from django.utils import timezone


class TransactionModel(models.Model):
    class TransactionType(models.TextChoices):
        DEBIT = 'DB', 'Debit'
        CREDIT = 'CR', 'Credit'

    account_id = models.IntegerField()
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=2,
        choices=TransactionType.choices,
        default=TransactionType.DEBIT,
    )

    def __str__(self):
        return f"{self.account_id} - {self.transaction_type} - {self.amount}"
