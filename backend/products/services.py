from django.db import transaction
from django.db.models import Q

from common.models import Sequence
from common.services import SequenceService
from core.db_context import get_current_database
from core.exceptions import NotFoundException
from products.models import Product


class ProductService:

    @classmethod
    def generate_product_code(cls, tenant_id):
        number = SequenceService.get_next_number(
            tenant_id=tenant_id,
            sequence_type=Sequence.SequenceType.PRODUCT,
        )

        return f"PROD{number:06d}"

    @classmethod
    def create_product(cls, validated_data):
        database = get_current_database()

        with transaction.atomic(using=database):
            tenant_id = validated_data["tenant_id"]
            validated_data["product_code"] = (cls.generate_product_code(tenant_id))
            product = Product.objects.using(database).create(**validated_data)

        return product

    @classmethod
    def get_products(cls,tenant_id,search=None,product_type=None,):
        database = get_current_database()

        queryset = Product.objects.using(database).filter(tenant_id=tenant_id,is_active=True,)

        if search:
            queryset = queryset.filter(
                Q(product_code__icontains=search)
                | Q(name__icontains=search)
                | Q(sku__icontains=search)
                | Q(hsn_code__icontains=search)
            )

        if product_type:
            queryset = queryset.filter(product_type=product_type)

        return queryset.order_by("-id")

    @classmethod
    def get_product_by_id(cls,tenant_id,product_id,):
        database = get_current_database()

        product = (Product.objects.using(database).filter(tenant_id=tenant_id,id=product_id,is_active=True,).first())

        if not product:
            raise NotFoundException("Product not found.")

        return product

    @classmethod
    def update_product(cls,product,validated_data,):
        database = get_current_database()

        with transaction.atomic(using=database):
            for field, value in validated_data.items():
                setattr(product, field, value)

            product.save(using=database,update_fields=[*validated_data.keys(),"updated_at",],)

        return product

    @classmethod
    def delete_product(cls, product):
        database = get_current_database()

        with transaction.atomic(using=database):
            product.is_active = False

            product.save(using=database,update_fields=["is_active","updated_at",],)

        return product