import asyncio
import time
import json
import requests
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.core.logger import logger

class ProductionTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        
    def run_scenario_tests(self) -> Dict[str, Any]:
        """Run comprehensive scenario tests"""
        scenarios = [
            {
                "name": "Agile fintech project",
                "query": "Help me plan an agile software development project for a fintech application",
                "expected_domain": "agile",
                "expected_sections": ["Overview", "Planning", "Execution"]
            },
            {
                "name": "ISO compliance audit",
                "query": "I need to conduct an ISO 27001 compliance audit for my organization",
                "expected_domain": "iso",
                "expected_sections": ["Risk Management", "Deliverables"]
            },
            {
                "name": "DevOps migration",
                "query": "Plan our DevOps migration from traditional infrastructure",
                "expected_domain": "devops",
                "expected_sections": ["Planning", "Execution"]
            },
            {
                "name": "High-risk banking app",
                "query": "Risk assessment for mobile banking application development",
                "expected_domain": "risk",
                "expected_sections": ["Risk Management"]
            },
            {
                "name": "Escalation scenario",
                "query": "Project is behind schedule and over budget, need escalation plan",
                "expected_domain": "planning",
                "expected_sections": ["Risk Management", "Planning"]
            },
            {
                "name": "Tool trigger - risk score",
                "query": "Calculate risk score for payment gateway integration",
                "expected_tool": "risk_score",
                "expected_sections": ["Risk Management"]
            },
            {
                "name": "Tool trigger - timeline",
                "query": "Estimate timeline for medium complexity team of 5",
                "expected_tool": "timeline",
                "expected_sections": ["Planning"]
            },
            {
                "name": "Tool trigger - document",
                "query": "Generate project document for our fintech system",
                "expected_tool": "document",
                "expected_sections": ["Deliverables"]
            },
            {
                "name": "Long input test",
                "query": "This is a very long query that tests the system's ability to handle extended user inputs. " * 50,
                "expected_sections": ["Overview", "Planning"]
            },
            {
                "name": "Empty context simulation",
                "query": "xyz123abc456def789 - very specific technical query",
                "expected_sections": ["Overview"]
            }
        ]
        
        results = {
            "total_scenarios": len(scenarios),
            "passed": 0,
            "failed": 0,
            "average_response_time": 0,
            "scenarios": []
        }
        
        total_time = 0
        
        for scenario in scenarios:
            result = self._run_single_scenario(scenario)
            results["scenarios"].append(result)
            total_time += result["response_time"]
            
            if result["passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        results["average_response_time"] = total_time / len(scenarios)
        results["success_rate"] = (results["passed"] / len(scenarios)) * 100
        
        return results
    
    def _run_single_scenario(self, scenario: Dict) -> Dict[str, Any]:
        """Run a single test scenario"""
        logger.info(f"Running scenario: {scenario['name']}")
        
        try:
            start_time = time.time()
            
            # Create session
            session_data = {
                "session_id": f"test_{int(time.time())}@test.com",
                "user_query": scenario["query"]
            }
            
            response = self.session.post(
                f"{self.base_url}/generate-prompt",
                json=session_data,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                passed = self._validate_scenario_response(data, scenario)
                
                return {
                    "name": scenario["name"],
                    "passed": passed,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "has_llm_response": bool(data.get("llm_response")),
                    "has_tool_output": bool(data.get("tool_output")),
                    "confidence_score": data.get("confidence_score", 0)
                }
            else:
                return {
                    "name": scenario["name"],
                    "passed": False,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            return {
                "name": scenario["name"],
                "passed": False,
                "response_time": 0,
                "error": str(e)
            }
    
    def _validate_scenario_response(self, data: Dict, scenario: Dict) -> bool:
        """Validate scenario response against expectations"""
        if not data.get("llm_response"):
            return False
        
        response_text = data["llm_response"].lower()
        
        # Check expected sections
        if "expected_sections" in scenario:
            for section in scenario["expected_sections"]:
                if section.lower() not in response_text:
                    return False
        
        # Check tool output
        if "expected_tool" in scenario:
            tool_output = data.get("tool_output")
            if not tool_output:
                return False
            
            if scenario["expected_tool"] == "risk_score" and "risk_score" not in str(tool_output):
                return False
            elif scenario["expected_tool"] == "timeline" and "estimated_duration" not in str(tool_output):
                return False
            elif scenario["expected_tool"] == "document" and "document_type" not in str(tool_output):
                return False
        
        return True
    
    def run_stress_test(self, concurrent_requests: int = 50) -> Dict[str, Any]:
        """Run stress test with concurrent requests"""
        logger.info(f"Starting stress test with {concurrent_requests} concurrent requests")
        
        def make_request(request_id: int) -> Dict[str, Any]:
            try:
                start_time = time.time()
                
                session_data = {
                    "session_id": f"stress_test_{request_id}_{int(time.time())}@test.com",
                    "user_query": f"Help me plan a software project (request {request_id})"
                }
                
                response = self.session.post(
                    f"{self.base_url}/generate-prompt",
                    json=session_data,
                    timeout=30
                )
                
                response_time = time.time() - start_time
                
                return {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                }
                
            except Exception as e:
                return {
                    "request_id": request_id,
                    "status_code": 0,
                    "response_time": 0,
                    "success": False,
                    "error": str(e)
                }
        
        # Run concurrent requests
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(concurrent_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        return {
            "concurrent_requests": concurrent_requests,
            "total_time": total_time,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": (len(successful_requests) / concurrent_requests) * 100,
            "requests_per_second": concurrent_requests / total_time,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "errors": [r.get("error") for r in failed_requests if r.get("error")]
        }
    
    def run_failure_tests(self) -> Dict[str, Any]:
        """Run failure scenario tests"""
        failure_scenarios = [
            {
                "name": "Invalid session ID",
                "data": {
                    "session_id": "invalid_session",
                    "user_query": "Test query"
                }
            },
            {
                "name": "Empty query",
                "data": {
                    "session_id": "test@example.com_1234567890",
                    "user_query": ""
                }
            },
            {
                "name": "Too long query",
                "data": {
                    "session_id": "test@example.com_1234567890",
                    "user_query": "x" * 3000
                }
            },
            {
                "name": "Malformed JSON",
                "data": "invalid json"
            }
        ]
        
        results = []
        
        for scenario in failure_scenarios:
            try:
                response = self.session.post(
                    f"{self.base_url}/generate-prompt",
                    json=scenario["data"] if isinstance(scenario["data"], dict) else scenario["data"],
                    timeout=10
                )
                
                results.append({
                    "name": scenario["name"],
                    "status_code": response.status_code,
                    "expected_failure": response.status_code >= 400,
                    "handled_properly": response.status_code >= 400
                })
                
            except Exception as e:
                results.append({
                    "name": scenario["name"],
                    "status_code": 0,
                    "expected_failure": True,
                    "handled_properly": True,
                    "exception": str(e)
                })
        
        return {
            "total_failure_scenarios": len(failure_scenarios),
            "handled_properly": len([r for r in results if r["handled_properly"]]),
            "results": results
        }
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        logger.info("Starting comprehensive production testing")
        
        report = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {
                "base_url": self.base_url,
                "python_version": "3.10",
                "test_framework": "ProductionTester v1.0"
            }
        }
        
        # Run scenario tests
        report["scenario_tests"] = self.run_scenario_tests()
        
        # Run stress tests
        report["stress_tests"] = {
            "concurrent_50": self.run_stress_test(50),
            "concurrent_100": self.run_stress_test(100)
        }
        
        # Run failure tests
        report["failure_tests"] = self.run_failure_tests()
        
        # Overall assessment
        scenario_success_rate = report["scenario_tests"]["success_rate"]
        stress_50_success_rate = report["stress_tests"]["concurrent_50"]["success_rate"]
        stress_100_success_rate = report["stress_tests"]["concurrent_100"]["success_rate"]
        failure_handling_rate = (report["failure_tests"]["handled_properly"] / report["failure_tests"]["total_failure_scenarios"]) * 100
        
        report["overall_assessment"] = {
            "scenario_performance": "Excellent" if scenario_success_rate >= 90 else "Good" if scenario_success_rate >= 80 else "Needs Improvement",
            "stress_performance": "Excellent" if stress_50_success_rate >= 95 and stress_100_success_rate >= 90 else "Good" if stress_50_success_rate >= 85 and stress_100_success_rate >= 80 else "Needs Improvement",
            "failure_handling": "Excellent" if failure_handling_rate >= 95 else "Good" if failure_handling_rate >= 85 else "Needs Improvement",
            "production_ready": (
                scenario_success_rate >= 80 and
                stress_50_success_rate >= 85 and
                stress_100_success_rate >= 80 and
                failure_handling_rate >= 85
            )
        }
        
        return report

if __name__ == "__main__":
    # Run tests
    tester = ProductionTester()
    report = tester.generate_test_report()
    
    print(json.dumps(report, indent=2))
    
    # Save report
    with open("production_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info("Production testing completed. Report saved to production_test_report.json")
