from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import json
import asyncio
from core.logger import LOGGER
from enum import Enum
from pydantic import BaseModel
from core.database_manager import DatabaseManager
from core.prompts.manager import PromptManager

# Load environment variables
load_dotenv()

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NEEDS_REVIEW = "needs_review"
    ERROR = "error"

class ComplianceResult(BaseModel):
    requirement_id: str
    status: ComplianceStatus
    confidence_score: float
    explanation: str
    suggested_actions: Optional[List[str]]

class ComplianceDocument(BaseModel):
    doc_id: str
    title: str
    requirements: List[Dict[str, str]]
    category: str
    version: str

class ComplianceChecker:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db_manager = DatabaseManager()
        self.prompt_manager = PromptManager()
        self.compliance_docs = self._load_compliance_documents()
        
    def _load_compliance_documents(self) -> List[ComplianceDocument]:
        """Load compliance documents from JSON file."""
        try:
            docs_data = self.db_manager.read_json_file("compliance_doc/doc.json")
            return [ComplianceDocument(**doc) for doc in docs_data["compliance_documents"]]
        except Exception as e:
            LOGGER.error(f"Error loading compliance documents: {str(e)}")
            raise

    async def _analyze_compliance(
        self,
        test_report: Dict[str, any],
        requirement: Dict[str, str]
    ) -> ComplianceResult:
        """Analyze a single requirement using OpenAI API."""
        try:
            prompt_template = await self.prompt_manager.load_prompt("compliance_analysis")
            prompt = prompt_template.format(
                test_report=json.dumps(test_report, indent=2),
                requirement_id=requirement['id'],
                requirement_description=requirement['description']
            )

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a compliance analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            analysis = json.loads(response.choices[0].message.content)
            
            return ComplianceResult(
                requirement_id=requirement['id'],
                status=ComplianceStatus(analysis['status']),
                confidence_score=analysis['confidence_score'],
                explanation=analysis['explanation'],
                suggested_actions=analysis.get('suggested_actions', [])
            )

        except Exception as e:
            LOGGER.error(f"Error analyzing compliance for requirement {requirement['id']}: {str(e)}")
            return ComplianceResult(
                requirement_id=requirement['id'],
                status=ComplianceStatus.ERROR,
                confidence_score=0.0,
                explanation=f"Error during analysis: {str(e)}",
                suggested_actions=["Review manually due to analysis error"]
            )

    async def check_compliance(
        self,
        test_report: Dict[str, any],
        categories: Optional[List[str]] = None
    ) -> Dict[str, List[ComplianceResult]]:
        """
        Check test report against all compliance documents or specific categories.
        """
        LOGGER.info(f"Starting compliance check for test report")
        results = {}

        try:
            for doc in self.compliance_docs:
                if categories and doc.category not in categories:
                    continue

                LOGGER.debug(f"Checking compliance against document: {doc.title}")
                doc_results = []

                for requirement in doc.requirements:
                    result = await self._analyze_compliance(test_report, requirement)
                    doc_results.append(result)

                results[doc.doc_id] = doc_results

            return results

        except Exception as e:
            LOGGER.error(f"Error during compliance check: {str(e)}")
            raise

    def generate_report(
        self,
        compliance_results: Dict[str, List[ComplianceResult]]
    ) -> Dict[str, any]:
        """Generate a summary report of compliance results."""
        try:
            report = {
                "summary": {
                    "total_checks": 0,
                    "compliant": 0,
                    "non_compliant": 0,
                    "needs_review": 0,
                    "errors": 0
                },
                "details": {}
            }

            for doc_id, results in compliance_results.items():
                report["details"][doc_id] = {
                    "results": [result.dict() for result in results],
                    "summary": {
                        "total": len(results),
                        "compliant": len([r for r in results if r.status == ComplianceStatus.COMPLIANT]),
                        "non_compliant": len([r for r in results if r.status == ComplianceStatus.NON_COMPLIANT]),
                        "needs_review": len([r for r in results if r.status == ComplianceStatus.NEEDS_REVIEW]),
                        "errors": len([r for r in results if r.status == ComplianceStatus.ERROR])
                    }
                }

                # Update overall summary
                report["summary"]["total_checks"] += len(results)
                report["summary"]["compliant"] += report["details"][doc_id]["summary"]["compliant"]
                report["summary"]["non_compliant"] += report["details"][doc_id]["summary"]["non_compliant"]
                report["summary"]["needs_review"] += report["details"][doc_id]["summary"]["needs_review"]
                report["summary"]["errors"] += report["details"][doc_id]["summary"]["errors"]

            LOGGER.info(f"Generated compliance report with {report['summary']['total_checks']} total checks")
            return report

        except Exception as e:
            LOGGER.error(f"Error generating compliance report: {str(e)}")
            raise

async def main():
    try:
        # Load test report from JSON
        with open("core/compliance_doc/test.json", "r") as f:
            test_report = json.load(f)

        # Initialize the compliance checker
        checker = ComplianceChecker()

        # Check compliance for both GDPR and DPDP
        results = await checker.check_compliance(
            test_report,
            categories=["gdpr", "dpdp", "common"]
        )

        # Generate detailed report
        report = checker.generate_report(results)

        # Save the results using database manager
        checker.db_manager.write_json_file(
            "compliance_doc/compliance_results.json", 
            report
        )

        # Log summary
        LOGGER.info(f"Compliance check completed. Summary:")
        LOGGER.info(f"Total checks: {report['summary']['total_checks']}")
        LOGGER.info(f"Compliant: {report['summary']['compliant']}")
        LOGGER.info(f"Non-compliant: {report['summary']['non_compliant']}")
        LOGGER.info(f"Needs review: {report['summary']['needs_review']}")
        LOGGER.info(f"Errors: {report['summary']['errors']}")

    except Exception as e:
        LOGGER.error(f"Error during compliance check: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
