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
import os
from dotenv import load_dotenv

load_dotenv()

# Add this temporarily to debug
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")

class ComplianceChecker(BaseAgent):
    def __init__(self, ai_model: str = "gpt-4"):
        self.agent_name = "ComplianceAgent"
        super().__init__(
            agent_name=self.agent_name,
            system_prompt_key="compliance_checker_system",
            ai_model=ai_model
        )

    def get_applicable_categories(self, location: str) -> List[str]:
        """Determine which compliance categories apply based on location."""
        categories = ["common"]  # Common requirements always apply
        if location.upper() in ["EU", "UK", "EUROPE"]:
            categories.append("gdpr")
        if location.upper() in ["INDIA", "IN"]:
            categories.append("dpdp")
        return categories

    async def analyze_compliance(
        self,
        test_data: Dict,
        requirement: Dict,
        location: str
    ) -> Optional[Dict]:
        """Analyze a single compliance requirement."""
        try:
            requirement_id = requirement.get('id')
            LOGGER.debug(f"Analyzing requirement {requirement_id} for location {location}")
            
            # Get the category from the requirement ID prefix
            category = requirement_id.split('.')[0].lower()
            
            prompt = prompt_manager.get_prompt(
                "prompt",  # Use the base prompt template
                location=location,
                test_report=json.dumps(test_data, indent=2),
                requirement_id=requirement_id,
                requirement_description=requirement.get('description', '')
            )
            
            LOGGER.debug(f"Sending prompt to LLM for requirement {requirement_id}")
            response = self.send_message(prompt)
            LOGGER.debug(f"Raw LLM response: {response}")
            
            # Try to extract JSON from the response
            try:
                # Find JSON content between curly braces
                json_str = response[response.find('{'):response.rfind('}')+1]
                analysis = json.loads(json_str)
            except json.JSONDecodeError:
                LOGGER.error(f"Failed to parse JSON from LLM response for requirement {requirement_id}")
                LOGGER.debug(f"Attempted to parse: {response}")
                return {
                    "requirement_id": requirement_id,
                    "category": category,
                    "status": "needs_review",
                    "confidence_score": 0.0,
                    "explanation": "Failed to parse LLM response",
                    "suggested_actions": ["Review requirement manually"]
                }

            return {
                "requirement_id": requirement_id,
                "category": category,
                "status": analysis.get('status', 'needs_review'),
                "confidence_score": analysis.get('confidence_score', 0.0),
                "explanation": analysis.get('explanation', 'No explanation provided'),
                "suggested_actions": analysis.get('suggested_actions', [])
            }

        except Exception as e:
            LOGGER.error(f"Error analyzing compliance for requirement {requirement.get('id', 'unknown')}: {str(e)}")
            LOGGER.debug(f"Full error details:", exc_info=True)
            return {
                "requirement_id": requirement.get('id', 'unknown'),
                "category": category if 'category' in locals() else 'unknown',
                "status": "needs_review",
                "confidence_score": 0.0,
                "explanation": f"Error during analysis: {str(e)}",
                "suggested_actions": ["Review requirement manually"]
            }

    async def check_compliance(
        self,
        test_data: Dict
    ) -> Dict[str, List[Dict]]:
        """Check test report against applicable compliance documents."""
        try:
            LOGGER.info(f"Starting compliance check for test ID: {test_data['test_id']}")
            
            location = test_data.get('location', 'UNKNOWN')
            applicable_categories = self.get_applicable_categories(location)
            
            LOGGER.info(f"Applicable categories for {location}: {applicable_categories}")
            
            # Load compliance documents
            with open("core/compliance_doc/doc.json", "r") as f:
                docs_data = json.load(f)
            compliance_docs = docs_data["compliance_documents"]
            
            results = {}
            for doc in compliance_docs:
                if doc["category"] not in applicable_categories:
                    continue

                LOGGER.debug(f"Checking compliance against document: {doc['title']}")
                doc_results = []

                analysis_tasks = [
                    self.analyze_compliance(test_data, requirement, location)
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
                "agent_name": self.agent_name,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_type": "Compliance Analysis"
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

async def run_analysis():
    checker = ComplianceChecker()
    
    # Load test report
    with open("core/compliance_doc/test.json", "r") as f:
        test_data = json.load(f)
    
    LOGGER.info(f"Starting compliance analysis for test ID: {test_data['test_id']}")
    
    # Run compliance check
    results = await checker.check_compliance(test_data)
    
    # Generate report with summary
    final_report = await checker.generate_report_summary(results)
    
    # Save report
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"core/compliance_doc/compliance_report_{test_data['test_id']}_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(final_report, f, indent=2)
    
    LOGGER.info(f"Analysis complete. Report saved to {filename}")
    return final_report

if __name__ == "__main__":
    report = asyncio.run(run_analysis())
    print(f"Compliance Rate: {report['summary']['compliance_rate']}%")
    print(f"Report saved with {report['summary']['total_requirements']} requirements analyzed")
