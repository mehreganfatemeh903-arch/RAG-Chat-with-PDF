from typing import Dict
import re


class InvoiceAnalyzer:
    """
    Extract basic invoice information.
    """

    def analyze(self, text: str) -> Dict:

        result = {
            "document_type": "invoice",
            "fields": {}
        }

        amount_patterns = [
            r"total\s*[:\-]?\s*([0-9,\.]+)",
            r"amount\s*[:\-]?\s*([0-9,\.]+)",
            r"مبلغ\s*[:\-]?\s*([0-9,\.]+)",
        ]

        for pattern in amount_patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                result["fields"]["total_amount"] = match.group(1)
                break


        date_patterns = [
            r"\d{4}[-/]\d{2}[-/]\d{2}",
            r"\d{2}[-/]\d{2}[-/]\d{4}",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)

            if match:
                result["fields"]["date"] = match.group()
                break


        result["fields"]["summary"] = (
            "Invoice document analyzed successfully"
        )

        return result