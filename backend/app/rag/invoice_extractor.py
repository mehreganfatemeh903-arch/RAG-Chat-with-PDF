import re
from typing import Any


def extract_invoice_fields(text: str) -> dict[str, Any]:
    fields = {
        "order_number": None,
        "order_date": None,
        "invoice_number": None,
        "customer_email": None,
        "customer_phone": None,
        "customer_address": None,
        "shipping_method": None,
        "item": None,
        "quantity": None,
        "unit_price": None,
        "total": None,
    }

    patterns = {
        "order_number": r"Order\s+Number\s*:\s*([^\s]+)",
        "order_date": r"Order\s+Date\s*:\s*(.+?)(?:\r?\n|$)",
        "customer_email": r"Billed\s+To\s*:\s*([^\s]+@[^\s]+)",
        "customer_phone": r"Customer\s+Phone\s+Number\s*:\s*([0-9]+)",
        "shipping_method": r"Shipping\s+method\s*:\s*(.+?)(?:\r?\n|$)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            fields[field] = match.group(1).strip()

    invoice = re.search(
        r"Invoice\s+(?:Number|No\.?)\s*:\s*([^\s]+)",
        text,
        re.IGNORECASE,
    )

    if invoice:
        fields["invoice_number"] = invoice.group(1).strip()

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    number_pattern = re.compile(
        r"^[0-9][0-9,]*(?:\.[0-9]+)?$"
    )

    table_start = None

    for index, line in enumerate(lines):
        if line.lower() == "item":
            table_start = index
            break

    if table_start is not None:
        table_lines = lines[table_start + 1:]

        numeric_values = []
        text_values = []

        for line in table_lines:
            if line.lower() in {
                "invoices this order",
                "thank you for your business!",
            }:
                break

            if number_pattern.fullmatch(line.replace(" ", "")):
                numeric_values.append(line.replace(" ", ""))
            elif not re.search(
                r"^(total|unit price|quantity|item)$",
                line,
                re.IGNORECASE,
            ):
                text_values.append(line)

        if text_values:
            fields["item"] = text_values[0]

        if len(numeric_values) >= 2:
            fields["unit_price"] = numeric_values[0]
            fields["total"] = numeric_values[1]

    if fields["total"] is None:
        total_matches = re.findall(
            r"(?:Total|Grand\s+Total)\s*[:\-]?\s*"
            r"([0-9][0-9,]*(?:\.[0-9]+)?)",
            text,
            re.IGNORECASE,
        )

        if total_matches:
            fields["total"] = total_matches[-1]

    return fields
