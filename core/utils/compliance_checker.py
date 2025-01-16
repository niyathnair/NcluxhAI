import sys
from pathlib import Path
# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
import json
import asyncio
from datetime import datetime
from core.logger import LOGGER
from typing import Dict, List, Optional
from agentcrew.base_agent import BaseAgent
from core.prompts.manager import prompt_manager



class ComplianceChecker(BaseAgent):
    def __init__(self, system_type: str, ai_model: str = "gpt-4"):
        self.system_type = system_type
        super().__init__(
            agent_name=f"{system_type.split('_')[0].title()}Agent",
            system_prompt_key=system_type,
            ai_model=ai_model
        )

    async def analyze_compliance(
        self,
        test_report: Dict,
        requirement: Dict[str, str]
    ) -> Optional[Dict]:
        """Analyze a single compliance requirement."""
        try:
            prompt = prompt_manager.get_prompt(
                "finance_legal",
                test_report=json.dumps(test_report, indent=2),
                requirement_id=requirement['id'],
                requirement_description=requirement['description']
            )
            
            response = self.send_message(prompt)
            analysis = json.loads(response)
            
            return {
                "requirement_id": requirement['id'],
                "status": analysis['status'],
                "confidence_score": analysis['confidence_score'],
                "explanation": analysis['explanation'],
                "suggested_actions": analysis.get('suggested_actions', [])
            }

        except Exception as e:
            LOGGER.error(f"Error analyzing compliance for requirement {requirement['id']}: {str(e)}")
            return None

    async def check_compliance(
        self,
        test_report: Dict,
        categories: Optional[List[str]] = None
    ) -> Dict[str, List[Dict]]:
        """Check test report against compliance documents."""
        try:
            LOGGER.info("Starting compliance check")
            
            # Load compliance documents directly from file
            with open("core/compliance_doc/doc.json", "r") as f:
                docs_data = json.load(f)
            compliance_docs = docs_data["compliance_documents"]
            
            results = {}
            for doc in compliance_docs:
                if categories and doc["category"] not in categories:
                    continue

                LOGGER.debug(f"Checking compliance against document: {doc['title']}")
                doc_results = []

                analysis_tasks = [
                    self.analyze_compliance(test_report, requirement)
                    for requirement in doc["requirements"]
                ]

                requirement_results = await asyncio.gather(*analysis_tasks)
                doc_results.extend([r for r in requirement_results if r is not None])
                
                if doc_results:
                    results[doc["doc_id"]] = doc_results

            return results

        except Exception as e:
            LOGGER.error(f"Error during compliance check: {str(e)}")
            raise

    async def generate_report_summary(self, results: Dict) -> Dict:
        """Generate a summary of compliance analysis."""
        total_requirements = 0
        compliant = 0
        non_compliant = 0
        needs_review = 0
        
        for doc_id, requirements in results.items():
            for req in requirements:
                total_requirements += 1
                if req['status'] == 'compliant':
                    compliant += 1
                elif req['status'] == 'non_compliant':
                    non_compliant += 1
                else:
                    needs_review += 1

        return {
            "report_metadata": {
                "system_type": self.system_type,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_type": self.system_type.split('_')[0].upper()
            },
            "summary": {
                "total_requirements": total_requirements,
                "compliant": compliant,
                "non_compliant": non_compliant,
                "needs_review": needs_review,
                "compliance_rate": round(compliant/total_requirements * 100, 2) if total_requirements > 0 else 0
            },
            "detailed_results": results
        }

async def run_analysis(system_type: str = "compliance_checker_system"):
    checker = ComplianceChecker(system_type)
    
    LOGGER.info(f"Starting compliance analysis with {system_type}")
    
    # Load test report directly from file
    with open("core/compliance_doc/test.json", "r") as f:
        test_report = json.load(f)
    
    # Run compliance check
    results = await checker.check_compliance(
        test_report,
        categories=["gdpr", "dpdp", "common"]
    )
    
    # Generate report with summary
    final_report = await checker.generate_report_summary(results)
    
    # Save report directly to file
    system_name = system_type.split('_')[0]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"core/compliance_doc/{system_name}_report_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(final_report, f, indent=2)
    
    LOGGER.info(f"Analysis complete. Report saved to {filename}")
    return final_report

if __name__ == "__main__":
    report = asyncio.run(run_analysis("gdpr_specialist_system"))
    print(f"Compliance Rate: {report['summary']['compliance_rate']}%")
    print(f"Report saved with {report['summary']['total_requirements']} requirements analyzed")
