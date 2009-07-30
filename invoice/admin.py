from django.contrib import admin
from django.conf.urls.defaults import patterns
from invoice.models import Invoice, InvoiceItem
from invoice.views import pdf_view


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem

class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline,]
    fieldsets = (
        (None, {
            'fields': ('user', 'address', 'status')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date', 'paid_date')
        }),
    )
    search_fields = ('invoice_id', 'user__username')
    list_filter = ('status',)
    list_display = (
        'invoice_id',
        'user',
        'invoice_date',
        'due_date',
        'status',
        'total_amount',
    )

    def get_urls(self):
        urls = super(InvoiceAdmin, self).get_urls()
        return patterns('',
            (r'^(.+)/pdf/$', self.admin_site.admin_view(pdf_view))
        ) + urls


admin.site.register(Invoice, InvoiceAdmin)