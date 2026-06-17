from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Customer
from shipments.models import (
    AuditLog,
    Payment,
    Shipment,
    ShipmentDocument,
    ShipmentTask,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data for the Client Portal Shipment module."

    def handle(self, *args, **options):
        customer, _ = Customer.objects.get_or_create(
            code="VN-GROW-CLIENT-20",
            defaults={"name": "Minh Long Co., Ltd"},
        )

        user, created = User.objects.get_or_create(
            email="khachhang@minhlong.vn",
            defaults={
                "full_name": "Minh Long Co., Ltd",
                "role": User.Role.CUSTOMER,
                "customer": customer,
            },
        )
        if created:
            user.set_password("demo1234")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created customer user."))

        admin, created = User.objects.get_or_create(
            email="admin@vngrow.vn",
            defaults={
                "full_name": "VNGROW Admin",
                "role": User.Role.MANAGER,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin1234")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created superuser admin@vngrow.vn."))

        if Shipment.objects.filter(customer=customer).exists():
            self.stdout.write("Shipments already seeded, skipping.")
            return

        today = date.today()
        samples = [
            {
                "code": "VGR-EXP-2406-001",
                "direction": Shipment.Direction.EXPORT,
                "mode": Shipment.Mode.FCL,
                "op_status": Shipment.OpStatus.CUSTOMS,
                "origin": "Ho Chi Minh, Vietnam",
                "destination": "Los Angeles, US",
                "item_name": "Roasted coffee beans",
                "quantity": "1,200 bags",
                "weight": "12,300 KGS",
                "cbm": "58 CBM",
                "container": "1 x 40'HC",
                "etd": today + timedelta(days=3),
                "eta": today + timedelta(days=27),
                "vessel": "EVER GIVEN",
                "voyage": "082E",
                "carrier": "Carrier A",
            },
            {
                "code": "VGR-IMP-2406-014",
                "direction": Shipment.Direction.IMPORT,
                "mode": Shipment.Mode.LCL,
                "op_status": Shipment.OpStatus.ARRIVED,
                "origin": "Shanghai, China",
                "destination": "Haiphong, Vietnam",
                "item_name": "Electronic components",
                "quantity": "85 cartons",
                "weight": "2,100 KGS",
                "cbm": "6.4 CBM",
                "container": "LCL",
                "etd": today - timedelta(days=12),
                "eta": today - timedelta(days=1),
                "vessel": "SITC HAIPHONG",
                "voyage": "2411N",
                "carrier": "SITC",
            },
            {
                "code": "VGR-EXP-2406-022",
                "direction": Shipment.Direction.EXPORT,
                "mode": Shipment.Mode.AIR,
                "op_status": Shipment.OpStatus.DEPARTED,
                "origin": "Ho Chi Minh, Vietnam",
                "destination": "Tokyo, Japan",
                "item_name": "Garments samples",
                "quantity": "8 boxes",
                "weight": "240 KGS",
                "cbm": "1.8 CBM",
                "container": "Air pallet",
                "etd": today + timedelta(days=5),
                "eta": today + timedelta(days=6),
                "vessel": "VN-NRT",
                "voyage": "VN300",
                "carrier": "Vietnam Airlines",
            },
        ]

        for data in samples:
            shipment = Shipment.objects.create(customer=customer, **data)
            tasks = [
                ("Tiếp nhận booking", Shipment.OpStatus.DEPARTED, "done"),
                ("Nhận chứng từ từ khách", "docs", "processing"),
                ("Khai báo hải quan", "customs", "pending"),
                ("Xác nhận cập cảng / giao hàng", "arrival", "pending"),
            ]
            for idx, (name, _key, st) in enumerate(tasks):
                ShipmentTask.objects.create(
                    shipment=shipment,
                    name=name,
                    date=today + timedelta(days=idx * 2),
                    status=st,
                    order=idx,
                )

            ShipmentDocument.objects.create(
                shipment=shipment,
                doc_type=ShipmentDocument.DocType.BILL,
                processing_status=ShipmentDocument.ProcessingStatus.COMPLETED,
                business_status=ShipmentDocument.BusinessStatus.RELEASED,
            )
            ShipmentDocument.objects.create(
                shipment=shipment,
                doc_type=ShipmentDocument.DocType.INVOICE,
                processing_status=ShipmentDocument.ProcessingStatus.REVIEW,
            )
            ShipmentDocument.objects.create(
                shipment=shipment,
                doc_type=ShipmentDocument.DocType.PACKING,
                processing_status=ShipmentDocument.ProcessingStatus.PENDING,
            )

            Payment.objects.create(
                shipment=shipment,
                currency="VND",
                total=45_600_000,
                paid=20_000_000,
                note="Đã tạm ứng đợt 1",
            )

            AuditLog.objects.create(
                shipment=shipment,
                actor="VNGROW Operation",
                action="Tạo shipment",
                detail="Khởi tạo hồ sơ lô hàng",
            )
            AuditLog.objects.create(
                shipment=shipment,
                actor="Minh Long Co., Ltd (khách)",
                action="Tải lên chứng từ",
                detail="Commercial Invoice - phiên bản V1",
            )

        self.stdout.write(self.style.SUCCESS("Seeded demo shipments."))
