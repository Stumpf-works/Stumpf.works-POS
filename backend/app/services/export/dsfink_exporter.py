"""
DSFinV-K Exporter
Export transaction data in DSFinV-K format for German tax authorities
"""

import csv
import io
import tarfile
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
import structlog

from app.models.transaction import Transaction, TransactionItem, TransactionStatus
from app.models.product import Product
from app.models.user import User
from app.models.tenant import Tenant

logger = structlog.get_logger()


class DSFinVKExporter:
    """
    DSFinV-K (Digitale Schnittstelle der Finanzverwaltung für Kassensysteme) Exporter.

    Generates compliant export files for German tax audits.
    Export format: TAR archive with CSV files.
    """

    def __init__(self, tenant_id: str, db: Session):
        self.tenant_id = tenant_id
        self.db = db

    def export(
        self,
        start_date: datetime,
        end_date: datetime,
        export_type: str = "full"
    ) -> bytes:
        """
        Create DSFinV-K export archive.

        Args:
            start_date: Start date for export
            end_date: End date for export
            export_type: Type of export ('full' or 'partial')

        Returns:
            TAR archive as bytes
        """
        logger.info(
            "dsfink_export_started",
            tenant_id=self.tenant_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Create TAR archive in memory
        tar_buffer = io.BytesIO()

        with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
            # Export each required CSV file
            files = {
                'stamm_orte.csv': self._export_locations(),
                'stamm_kassen.csv': self._export_cash_registers(),
                'stamm_mitarbeiter.csv': self._export_employees(),
                'stamm_artikel.csv': self._export_products(),
                'bonkopf.csv': self._export_transaction_headers(start_date, end_date),
                'bonpos.csv': self._export_transaction_items(start_date, end_date),
                'tse_transaktionen.csv': self._export_tse_transactions(start_date, end_date),
            }

            for filename, content in files.items():
                # Add file to TAR
                info = tarfile.TarInfo(name=filename)
                info.size = len(content.encode('utf-8'))
                info.mtime = datetime.now().timestamp()

                tar.addfile(info, io.BytesIO(content.encode('utf-8')))

        tar_buffer.seek(0)
        result = tar_buffer.getvalue()

        logger.info(
            "dsfink_export_completed",
            tenant_id=self.tenant_id,
            size_bytes=len(result),
        )

        return result

    def _export_locations(self) -> str:
        """Export locations (Orte) as CSV."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Header
        writer.writerow([
            'LOC_ID',
            'LOC_NAME',
            'LOC_STREET',
            'LOC_POSTAL_CODE',
            'LOC_CITY',
            'LOC_COUNTRY',
        ])

        # Get tenant data
        tenant = self.db.query(Tenant).filter(Tenant.slug == self.tenant_id).first()

        if tenant:
            writer.writerow([
                1,
                tenant.name,
                tenant.address_street or '',
                tenant.address_postal_code or '',
                tenant.address_city or '',
                tenant.address_country or 'DE',
            ])

        return output.getvalue()

    def _export_cash_registers(self) -> str:
        """Export cash registers (Kassen) as CSV."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Header
        writer.writerow([
            'CASH_REGISTER_ID',
            'CASH_REGISTER_TYPE',
            'CASH_REGISTER_SERIAL',
            'CASH_REGISTER_BRAND',
            'CASH_REGISTER_MODEL',
            'CASH_REGISTER_SOFTWARE_VERSION',
            'CASH_REGISTER_BASE_CURRENCY',
        ])

        # Single cash register for now
        writer.writerow([
            'POS-1',
            'PC-Kasse',
            'STUMPF-001',
            'Stumpf.works',
            'POS v1.0',
            '1.0.0',
            'EUR',
        ])

        return output.getvalue()

    def _export_employees(self) -> str:
        """Export employees (Mitarbeiter) as CSV."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Header
        writer.writerow([
            'EMPLOYEE_ID',
            'EMPLOYEE_NAME',
            'EMPLOYEE_ROLE',
        ])

        # Get users
        users = self.db.query(User).filter(User.tenant_id == self.tenant_id).all()

        for user in users:
            writer.writerow([
                user.id,
                f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                user.role.value,
            ])

        return output.getvalue()

    def _export_products(self) -> str:
        """Export products (Artikel) as CSV."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Header
        writer.writerow([
            'ARTICLE_ID',
            'ARTICLE_NUMBER',
            'ARTICLE_NAME',
            'ARTICLE_GROUP',
            'ARTICLE_PRICE',
            'ARTICLE_VAT_RATE',
        ])

        # Get products
        products = self.db.query(Product).filter(Product.tenant_id == self.tenant_id).all()

        for product in products:
            writer.writerow([
                product.id,
                product.sku or product.barcode or '',
                product.name,
                product.category_id or '',
                f"{product.price:.2f}",
                product.vat_rate.value,
            ])

        return output.getvalue()

    def _export_transaction_headers(self, start_date: datetime, end_date: datetime) -> str:
        """Export transaction headers (Bonköpfe) as CSV."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Header
        writer.writerow([
            'BON_ID',
            'BON_NR',
            'BON_TYPE',
            'BON_DATE',
            'BON_TIME',
            'CASH_REGISTER_ID',
            'EMPLOYEE_ID',
            'BON_TOTAL',
            'BON_CURRENCY',
            'BON_PAYMENT_METHOD',
            'TSE_SIGNATURE_COUNTER',
            'TSE_TRANSACTION_NUMBER',
        ])

        # Get transactions
        transactions = self.db.query(Transaction).filter(
            Transaction.tenant_id == self.tenant_id,
            Transaction.completed_at >= start_date,
            Transaction.completed_at <= end_date,
            Transaction.status == TransactionStatus.COMPLETED
        ).all()

        for txn in transactions:
            writer.writerow([
                txn.id,
                txn.receipt_number,
                'Beleg',
                txn.completed_at.strftime('%Y-%m-%d'),
                txn.completed_at.strftime('%H:%M:%S'),
                'POS-1',
                txn.user_id,
                f"{txn.total:.2f}",
                'EUR',
                txn.payment_method.value,
                txn.tse_signature or '',
                txn.tse_transaction_id or '',
            ])

        return output.getvalue()

    def _export_transaction_items(self, start_date: datetime, end_date: datetime) -> str:
        """Export transaction items (Bonpositionen) as CSV."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Header
        writer.writerow([
            'BON_ID',
            'POS_LINE',
            'ARTICLE_ID',
            'ARTICLE_NUMBER',
            'ARTICLE_NAME',
            'QUANTITY',
            'UNIT_PRICE',
            'VAT_RATE',
            'LINE_TOTAL',
        ])

        # Get transactions with items
        transactions = self.db.query(Transaction).filter(
            Transaction.tenant_id == self.tenant_id,
            Transaction.completed_at >= start_date,
            Transaction.completed_at <= end_date,
            Transaction.status == TransactionStatus.COMPLETED
        ).all()

        for txn in transactions:
            for idx, item in enumerate(txn.items, start=1):
                writer.writerow([
                    txn.id,
                    idx,
                    item.product_id,
                    item.product_sku or '',
                    item.product_name,
                    item.quantity,
                    f"{item.unit_price:.2f}",
                    f"{item.vat_rate:.2f}",
                    f"{item.total:.2f}",
                ])

        return output.getvalue()

    def _export_tse_transactions(self, start_date: datetime, end_date: datetime) -> str:
        """Export TSE transactions as CSV."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Header
        writer.writerow([
            'BON_ID',
            'TSE_TRANSACTION_NUMBER',
            'TSE_SIGNATURE_COUNTER',
            'TSE_SIGNATURE',
            'TSE_START_TIME',
            'TSE_END_TIME',
            'TSE_SERIAL_NUMBER',
        ])

        # Get signed transactions
        transactions = self.db.query(Transaction).filter(
            Transaction.tenant_id == self.tenant_id,
            Transaction.completed_at >= start_date,
            Transaction.completed_at <= end_date,
            Transaction.is_tse_signed == True
        ).all()

        for txn in transactions:
            writer.writerow([
                txn.id,
                txn.tse_transaction_id or '',
                txn.tse_signature or '',
                txn.tse_signature or '',
                txn.tse_time_start.strftime('%Y-%m-%d %H:%M:%S') if txn.tse_time_start else '',
                txn.tse_time_end.strftime('%Y-%m-%d %H:%M:%S') if txn.tse_time_end else '',
                txn.tse_serial_number or '',
            ])

        return output.getvalue()
