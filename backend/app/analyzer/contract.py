from typing import Dict
import re


class ContractAnalyzer:
    """
    Analyze contracts and extract important clauses.
    """

    def analyze(self, text: str) -> Dict:

        fields = {}

        keywords = {
            "parties": [
                "between",
                "party",
                "طرفین"
            ],
            "obligations": [
                "obligation",
                "responsibility",
                "تعهد"
            ],
            "termination": [
                "termination",
                "cancel",
                "فسخ"
            ]
        }

        for name, words in keywords.items():

            found = []

            for word in words:
                if word.lower() in text.lower():
                    found.append(word)

            fields[name] = found

        dates = re.findall(
            r"\d{4}[-/]\d{2}[-/]\d{2}",
            text
        )

        fields["dates"] = dates

        return {
            "document_type": "contract",
            "fields": fields,
            "summary": "Contract analysis completed"
        }
