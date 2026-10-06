from typing import Dict


class DocumentTypeDetector:
    """
    Detect document category based on extracted text.
    """

    KEYWORDS = {
        "invoice": [
            "invoice",
            "bill",
            "total",
            "amount",
            "tax",
            "قیمت",
            "فاکتور",
            "مالیات",
        ],
        "contract": [
            "agreement",
            "contract",
            "party",
            "signature",
            "terms",
            "قرارداد",
            "امضا",
            "تعهد",
        ],
        "resume": [
            "resume",
            "cv",
            "experience",
            "education",
            "skills",
            "مهارت",
            "سابقه",
            "تحصیلات",
        ],
    }

    def detect(self, text: str) -> Dict:
        text_lower = text.lower()

        scores = {}

        for doc_type, words in self.KEYWORDS.items():
            score = 0

            for word in words:
                if word.lower() in text_lower:
                    score += 1

            scores[doc_type] = score

        detected_type = max(
            scores,
            key=scores.get
        )

        confidence = 0

        if scores[detected_type] > 0:
            confidence = min(
                scores[detected_type] / 5,
                1
            )

        return {
            "document_type": detected_type,
            "confidence": round(confidence, 2),
            "scores": scores,
        }
