from typing import Dict
import re


class ResumeAnalyzer:
    """
    Analyze CV / Resume documents.
    """

    def analyze(self, text: str) -> Dict:

        fields = {}

        sections = {
            "skills": [
                "skills",
                "skill",
                "مهارت",
                "technologies",
            ],
            "experience": [
                "experience",
                "work",
                "سابقه",
                "تجربه",
            ],
            "education": [
                "education",
                "degree",
                "تحصیلات",
                "مدرک",
            ],
        }

        text_lower = text.lower()

        for section, keywords in sections.items():

            matched = []

            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matched.append(keyword)

            fields[section] = matched

        emails = re.findall(
            r'[\w\.-]+@[\w\.-]+\.\w+',
            text
        )

        if emails:
            fields["email"] = emails[0]

        phones = re.findall(
            r'\+?\d[\d\s\-]{8,}',
            text
        )

        if phones:
            fields["phone"] = phones[0]

        return {
            "document_type": "resume",
            "fields": fields,
            "summary": "Resume analysis completed"
        }
