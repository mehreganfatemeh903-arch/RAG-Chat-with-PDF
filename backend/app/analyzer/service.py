import json
from typing import Dict

from sqlalchemy.orm import Session

from app.analyzer.detector import DocumentTypeDetector
from app.analyzer.invoice import InvoiceAnalyzer
from app.analyzer.contract import ContractAnalyzer
from app.analyzer.resume import ResumeAnalyzer
from app.extraction.models import DocumentAnalysis


class DocumentAnalyzerService:

    def __init__(self):

        self.detector = DocumentTypeDetector()

        self.analyzers = {
            "invoice": InvoiceAnalyzer(),
            "contract": ContractAnalyzer(),
            "resume": ResumeAnalyzer(),
        }


    def analyze(self, text: str) -> Dict:

        detection = self.detector.detect(text)

        document_type = detection["document_type"]

        analyzer = self.analyzers.get(
            document_type
        )

        if analyzer:
            result = analyzer.analyze(text)
        else:
            result = {
                "document_type": document_type,
                "fields": {},
                "summary": "Generic document analyzed"
            }


        return {
            "detection": detection,
            "analysis": result
        }


    def save_analysis(
        self,
        db: Session,
        document_id: int,
        result: Dict
    ):

        detection = result["detection"]

        analysis = DocumentAnalysis(
            document_id=document_id,
            document_type=detection["document_type"],
            extracted_data=json.dumps(
                result["analysis"],
                ensure_ascii=False
            ),
            confidence=detection["confidence"]
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return analysis