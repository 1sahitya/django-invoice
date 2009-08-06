from datetime import date
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django_extensions.db.models import TimeStampedModel

from addressbook.models import Address
from invoice.utils import friendly_id
from invoice.utils.format import format_currency


class Invoice(TimeStampedModel):
    STATUSES = [
        ('draft', 'Draft'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
    ]
    user = models.ForeignKey(User)
    address = models.ForeignKey(Address, related_name='%(class)s_set')
    status = models.CharField(max_length=20, choices=STATUSES, default='draft')

    invoice_id = models.CharField(max_length=6, null=True, blank=True, unique=True, editable=False)
    invoice_date = models.DateField(default=date.today)
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)


    def __unicode__(self):
        return u'%s (%s)' % (self.invoice_id, self.total_amount())

    def total_amount(self):
        return format_currency(self.total())

    def total(self):
        total = Decimal('0.00')
        for item in self.items.all():
            total = total + item.total()
        return total


    def save(self, *args, **kwargs):
        if self.status == 'paid' and not self.paid_date:
            self.paid_date = date.today()

        super(Invoice, self).save(*args, **kwargs)

        if not self.invoice_id:
            self.invoice_id = friendly_id.encode(self.pk)
            super(Invoice, self).save(*args, **kwargs)


    class Meta:
        ordering = ('-invoice_date', 'id')


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', unique=False)
    description = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=1)


    def total(self):
        return Decimal(str(self.unit_price * self.quantity)).quantize(Decimal('0.01'))


    def __unicode__(self):
        return self.description
