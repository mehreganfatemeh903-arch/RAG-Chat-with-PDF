from app.analyzer.service import DocumentAnalyzerService


service = DocumentAnalyzerService()


text = """
Invoice
Total: 2500
Tax: 200
Date: 2026-10-04
"""


result = service.analyze(text)

print(result)