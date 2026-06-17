from django.db.models import Max
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import AuditLog, Shipment, ShipmentDocument
from .serializers import (
    ShipmentDetailSerializer,
    ShipmentDocumentSerializer,
    ShipmentListSerializer,
)


class ShipmentViewSet(viewsets.ReadOnlyModelViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        qs = Shipment.objects.all()
        # Customers only see their own company's shipments.
        if user.role == user.Role.CUSTOMER and user.customer_id:
            qs = qs.filter(customer_id=user.customer_id)

        params = self.request.query_params
        direction = params.get("direction")
        if direction:
            qs = qs.filter(direction=direction)
        mode = params.get("mode")
        if mode:
            qs = qs.filter(mode=mode)
        op_status = params.get("op_status")
        if op_status:
            qs = qs.filter(op_status=op_status)

        ordering = params.get("ordering")
        if ordering == "eta":
            qs = qs.order_by("eta")
        elif ordering == "etd":
            qs = qs.order_by("etd")
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ShipmentListSerializer
        return ShipmentDetailSerializer

    @action(detail=True, methods=["post"], url_path="documents")
    def upload_document(self, request, pk=None):
        shipment = self.get_object()
        doc_type = request.data.get("doc_type")
        upload = request.data.get("file")
        if not doc_type or not upload:
            return Response(
                {"detail": "doc_type và file là bắt buộc."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        last_version = (
            ShipmentDocument.objects.filter(
                shipment=shipment, doc_type=doc_type
            ).aggregate(m=Max("version"))["m"]
            or 0
        )
        document = ShipmentDocument.objects.create(
            shipment=shipment,
            doc_type=doc_type,
            file=upload,
            version=last_version + 1,
            processing_status=ShipmentDocument.ProcessingStatus.REVIEW,
            uploaded_by=request.user,
        )
        AuditLog.objects.create(
            shipment=shipment,
            actor=request.user.email,
            action="Tải lên chứng từ",
            detail=f"{document.get_doc_type_display()} - phiên bản V{document.version}",
        )
        return Response(
            ShipmentDocumentSerializer(document).data,
            status=status.HTTP_201_CREATED,
        )
