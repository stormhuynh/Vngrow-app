from rest_framework import serializers

from .models import AuditLog, Payment, Shipment, ShipmentDocument, ShipmentTask


class ShipmentTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ShipmentTask
        fields = [
            "id",
            "name",
            "date",
            "actual_date",
            "status",
            "status_display",
            "note",
            "order",
        ]


class ShipmentDocumentSerializer(serializers.ModelSerializer):
    doc_type_display = serializers.CharField(
        source="get_doc_type_display", read_only=True
    )
    processing_status_display = serializers.CharField(
        source="get_processing_status_display", read_only=True
    )
    business_status_display = serializers.CharField(
        source="get_business_status_display", read_only=True
    )
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ShipmentDocument
        fields = [
            "id",
            "doc_type",
            "doc_type_display",
            "processing_status",
            "processing_status_display",
            "business_status",
            "business_status_display",
            "file",
            "version",
            "uploaded_by_name",
            "uploaded_at",
        ]
        read_only_fields = ["version", "uploaded_at"]

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.full_name or obj.uploaded_by.email
        return ""


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["currency", "total", "paid", "proof", "note", "updated_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "timestamp", "actor", "action", "detail"]


class ShipmentListSerializer(serializers.ModelSerializer):
    direction_display = serializers.CharField(
        source="get_direction_display", read_only=True
    )
    mode_display = serializers.CharField(source="get_mode_display", read_only=True)
    op_status_display = serializers.CharField(
        source="get_op_status_display", read_only=True
    )
    current_task_name = serializers.SerializerMethodField()
    current_task_status = serializers.SerializerMethodField()
    current_task_status_display = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            "id",
            "code",
            "direction",
            "direction_display",
            "mode",
            "mode_display",
            "op_status",
            "op_status_display",
            "current_task_name",
            "current_task_status",
            "current_task_status_display",
            "origin",
            "destination",
            "etd",
            "eta",
            "carrier",
        ]

    def get_current_task_name(self, obj):
        task = obj.get_current_progress_task()
        if task:
            return task.name
        return ""

    def get_current_task_status(self, obj):
        task = obj.get_current_progress_task()
        if task:
            return task.status
        return ""

    def get_current_task_status_display(self, obj):
        task = obj.get_current_progress_task()
        if task:
            return task.get_status_display()
        return ""


class ShipmentDetailSerializer(ShipmentListSerializer):
    tasks = ShipmentTaskSerializer(many=True, read_only=True)
    documents = ShipmentDocumentSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    audit_logs = AuditLogSerializer(many=True, read_only=True)

    class Meta(ShipmentListSerializer.Meta):
        fields = ShipmentListSerializer.Meta.fields + [
            "item_name",
            "quantity",
            "weight",
            "cbm",
            "container",
            "vessel",
            "voyage",
            "si_cutoff",
            "vgm_cutoff",
            "tasks",
            "documents",
            "payment",
            "audit_logs",
        ]
