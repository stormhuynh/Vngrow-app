from django.conf import settings
from django.db import models
from django.utils import timezone


class Shipment(models.Model):
    class Direction(models.TextChoices):
        EXPORT = "export", "Export"
        IMPORT = "import", "Import"

    class Mode(models.TextChoices):
        FCL = "fcl", "FCL"
        LCL = "lcl", "LCL"
        AIR = "air", "Air cargo"
        EXPRESS = "express", "Express"

    class OpStatus(models.TextChoices):
        DEPARTED = "departed", "Khởi hành"
        DOCS_RECEIVING = "docs_receiving", "Tiếp nhận chứng từ"
        CUSTOMS = "customs", "Khai hải quan"
        ARRIVED = "arrived", "Đã cập cảng"

    code = models.CharField(max_length=40, unique=True)
    customer = models.ForeignKey(
        "accounts.Customer", on_delete=models.CASCADE, related_name="shipments"
    )
    direction = models.CharField(max_length=10, choices=Direction.choices)
    mode = models.CharField(max_length=10, choices=Mode.choices)
    op_status = models.CharField(
        max_length=20, choices=OpStatus.choices, default=OpStatus.DEPARTED
    )

    origin = models.CharField(max_length=120, blank=True)
    destination = models.CharField(max_length=120, blank=True)

    # Mô tả hàng hóa
    item_name = models.CharField(max_length=200, blank=True)
    quantity = models.CharField(max_length=80, blank=True)
    weight = models.CharField(max_length=80, blank=True)
    cbm = models.CharField(max_length=80, blank=True)
    container = models.CharField(max_length=120, blank=True)

    # Thông tin vận chuyển
    etd = models.DateField(null=True, blank=True)
    eta = models.DateField(null=True, blank=True)
    vessel = models.CharField(max_length=120, blank=True)
    voyage = models.CharField(max_length=80, blank=True)
    carrier = models.CharField(max_length=120, blank=True)

    si_cutoff = models.DateTimeField(null=True, blank=True)
    vgm_cutoff = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    def sync_op_status_from_tasks(self):
        task = self.get_current_progress_task()
        if not task:
            return
        next_status = self.map_task_to_op_status(task)
        if self.op_status != next_status:
            self.op_status = next_status
            self.save(update_fields=["op_status", "updated_at"])

    def get_current_progress_task(self):
        today = timezone.localdate()
        return min(
            self.tasks.filter(
                status__in=[
                    ShipmentTask.Status.PROCESSING,
                    ShipmentTask.Status.DONE,
                ],
                date__isnull=False,
            ),
            key=lambda item: (abs((item.date - today).days), -item.date.toordinal()),
            default=None,
        )

    def map_task_to_op_status(self, task):
        name = task.name.lower()
        if "cập cảng" in name or "giao hàng" in name or "arrival" in name:
            return self.OpStatus.ARRIVED
        if "hải quan" in name or "customs" in name:
            return self.OpStatus.CUSTOMS
        if "chứng từ" in name or "document" in name or "docs" in name:
            return self.OpStatus.DOCS_RECEIVING
        return self.OpStatus.DEPARTED


class ShipmentTask(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Chờ"
        PROCESSING = "processing", "Đang xử lí"
        DONE = "done", "Hoàn thành"

    shipment = models.ForeignKey(
        Shipment, on_delete=models.CASCADE, related_name="tasks"
    )
    name = models.CharField(max_length=200)
    date = models.DateField(null=True, blank=True)
    actual_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    note = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.shipment.code} - {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.shipment.sync_op_status_from_tasks()

    def delete(self, *args, **kwargs):
        shipment = self.shipment
        result = super().delete(*args, **kwargs)
        shipment.sync_op_status_from_tasks()
        return result


class ShipmentDocument(models.Model):
    class DocType(models.TextChoices):
        BILL = "bill", "Bill of Lading"
        INVOICE = "invoice", "Commercial Invoice"
        PACKING = "packing", "Packing List"
        CO = "co", "Certificate of Origin"
        CONTRACT = "contract", "Sales contract / Proforma invoice"
        OTHER = "other", "Khác"

    class ProcessingStatus(models.TextChoices):
        PENDING = "pending", "Chờ nộp"
        REVIEW = "review", "Review"
        REVISION = "revision", "Revision"
        COMPLETED = "completed", "Completed"

    class BusinessStatus(models.TextChoices):
        NONE = "none", "--"
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        RELEASED = "released", "Released"

    shipment = models.ForeignKey(
        Shipment, on_delete=models.CASCADE, related_name="documents"
    )
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    processing_status = models.CharField(
        max_length=12,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
    )
    business_status = models.CharField(
        max_length=12,
        choices=BusinessStatus.choices,
        default=BusinessStatus.NONE,
    )
    file = models.FileField(upload_to="documents/%Y/%m/", null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["doc_type", "-version"]

    def __str__(self):
        return f"{self.shipment.code} - {self.get_doc_type_display()} v{self.version}"


class Payment(models.Model):
    shipment = models.OneToOneField(
        Shipment, on_delete=models.CASCADE, related_name="payment"
    )
    currency = models.CharField(max_length=8, default="VND")
    total = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    proof = models.FileField(upload_to="payments/%Y/%m/", null=True, blank=True)
    note = models.CharField(max_length=300, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.shipment.code}"


class AuditLog(models.Model):
    shipment = models.ForeignKey(
        Shipment, on_delete=models.CASCADE, related_name="audit_logs"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.CharField(max_length=160)
    action = models.CharField(max_length=200)
    detail = models.CharField(max_length=400, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.shipment.code} - {self.action}"
