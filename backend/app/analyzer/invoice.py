from typing import Dict

from app.rag.invoice_extractor import extract_invoice_fields


class InvoiceAnalyzer:
    """
    Extract structured invoice information.
    """

    def analyze(self, text: str) -> Dict:
        fields = extract_invoice_fields(text)

        return {
            "document_type": "invoice",
            "fields": fields,
            "summary": "Invoice document analyzed successfully",
        }
