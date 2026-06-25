import polars as pl

from core.enums import FileType
from ingestion.types import ValidationIssue, ValidationReport


def validate_relationships(frames: dict[FileType, pl.DataFrame], report: ValidationReport) -> None:
    subscriptions = frames.get(FileType.SUBSCRIPTIONS)
    invoices = frames.get(FileType.INVOICES)
    line_items = frames.get(FileType.INVOICE_LINE_ITEMS)

    if subscriptions is not None and "customer_id" in subscriptions.columns:
        customer_ids = set(subscriptions["customer_id"].drop_nulls().cast(pl.Utf8).to_list())
    else:
        customer_ids = set()

    if invoices is not None and "customer_id" in invoices.columns:
        invoice_customers = set(invoices["customer_id"].drop_nulls().cast(pl.Utf8).to_list())
        if customer_ids:
            orphans = invoice_customers - customer_ids
            if orphans:
                sample = list(orphans)[:5]
                report.issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="orphan_invoice_customer",
                        message=f"Invoices reference unknown customers: {sample}",
                        file_type=FileType.INVOICES.value,
                    )
                )

    if invoices is not None and line_items is not None:
        if "invoice_id" in invoices.columns and "invoice_id" in line_items.columns:
            invoice_ids = set(invoices["invoice_id"].drop_nulls().cast(pl.Utf8).to_list())
            line_invoice_ids = set(line_items["invoice_id"].drop_nulls().cast(pl.Utf8).to_list())
            orphans = line_invoice_ids - invoice_ids
            if orphans:
                sample = list(orphans)[:5]
                report.issues.append(
                    ValidationIssue(
                        severity="blocking",
                        code="orphan_line_item_invoice",
                        message=f"Line items reference unknown invoices: {sample}",
                        file_type=FileType.INVOICE_LINE_ITEMS.value,
                    )
                )

    if subscriptions is not None and invoices is not None:
        if "subscription_id" in subscriptions.columns and "subscription_id" in invoices.columns:
            sub_ids = set(subscriptions["subscription_id"].drop_nulls().cast(pl.Utf8).to_list())
            inv_sub_ids = set(invoices["subscription_id"].drop_nulls().cast(pl.Utf8).to_list()) - {""}
            orphans = inv_sub_ids - sub_ids
            if orphans:
                sample = list(orphans)[:5]
                report.issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="orphan_invoice_subscription",
                        message=f"Invoices reference unknown subscriptions: {sample}",
                        file_type=FileType.INVOICES.value,
                    )
                )
