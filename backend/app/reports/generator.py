from datetime import datetime


class ReportGenerator:

    def generate(self, analysis: dict):

        report = {
            "created_at": datetime.utcnow().isoformat(),
            "title": "AI Document Analysis Report",
            "document_type":
                analysis.get("document_type"),

            "summary":
                analysis.get("summary"),

            "details":
                analysis.get("fields", {})
        }

        return report