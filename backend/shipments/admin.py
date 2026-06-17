from django.contrib import admin

from .models import AuditLog, Payment, Shipment, ShipmentDocument, ShipmentTask


class ShipmentTaskInline(admin.TabularInline):
    model = ShipmentTask
    extra = 0


class ShipmentDocumentInline(admin.TabularInline):
    model = ShipmentDocument
    extra = 0


class AuditLogInline(admin.TabularInline):
    model = AuditLog
    extra = 0
    readonly_fields = ("timestamp",)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("code", "customer", "direction", "mode", "op_status", "etd", "eta")
    list_filter = ("direction", "mode")
    search_fields = ("code", "customer__name", "carrier", "vessel")
    exclude = ("op_status",)
    inlines = [ShipmentTaskInline, ShipmentDocumentInline, AuditLogInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.sync_op_status_from_tasks()


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("shipment", "currency", "total", "paid", "updated_at")


@admin.register(ShipmentDocument)
class ShipmentDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "shipment",
        "doc_type",
        "processing_status",
        "business_status",
        "version",
        "uploaded_at",
    )
    list_filter = ("doc_type", "processing_status", "business_status")
