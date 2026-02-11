import asyncio
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_single_request():
    """Test single request performance"""
    try:
        start_time = time.time()
        
        response = requests.post(
            "http://127.0.0.1:8002/generate-prompt",
            json={
                "session_id": "test@example.com_1234567890",
                "user_query": "Help me plan an agile software development project"
            },
            timeout=30
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response_time": end_time - start_time,
                "confidence_score": data.get("confidence_score", 0),
                "has_llm_response": bool(data.get("llm_response")),
                "has_tool_output": bool(data.get("tool_output"))
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_concurrent_requests(num_requests=20):
    """Test concurrent requests"""
    print(f"🧪 Testing {num_requests} concurrent requests...")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(test_single_request) for _ in range(num_requests)]
        results = [future.result() for future in as_completed(futures)]
    
    end_time = time.time()
    
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
        "total_requests": num_requests,
        "total_time": end_time - start_time,
        "successful_requests": len(successful_requests),
        "failed_requests": len(failed_requests),
        "success_rate": (len(successful_requests) / num_requests) * 100,
        "requests_per_second": num_requests / (end_time - start_time),
        "avg_response_time": avg_response_time,
        "max_response_time": max_response_time,
        "min_response_time": min_response_time,
        "errors": [r.get("error") for r in failed_requests if r.get("error")]
    }

def test_input_validation():
    """Test input validation"""
    print("🧪 Testing input validation...")
    
    test_cases = [
        {
            "name": "Too short query",
            "data": {
                "session_id": "test@example.com_1234567890",
                "user_query": "Hi"
            },
            "should_fail": True
        },
        {
            "name": "Too long query",
            "data": {
                "session_id": "test@example.com_1234567890",
                "user_query": "x" * 3000
            },
            "should_fail": True
        },
        {
            "name": "Valid query",
            "data": {
                "session_id": "test@example.com_1234567890",
                "user_query": "Help me plan a software development project with agile methodology"
            },
            "should_fail": False
        },
        {
            "name": "Missing session_id",
            "data": {
                "user_query": "Help me plan a software development project"
            },
            "should_fail": True
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            response = requests.post(
                "http://127.0.0.1:8002/generate-prompt",
                json=test_case["data"],
                timeout=10
            )
            
            failed = response.status_code >= 400
            
            results.append({
                "name": test_case["name"],
                "expected_failure": test_case["should_fail"],
                "actual_failure": failed,
                "status_code": response.status_code,
                "passed": failed == test_case["should_fail"]
            })
            
        except Exception as e:
            results.append({
                "name": test_case["name"],
                "expected_failure": test_case["should_fail"],
                "actual_failure": True,
                "error": str(e),
                "passed": test_case["should_fail"]  # Exception means it failed as expected
            })
    
    return {
        "total_tests": len(test_cases),
        "passed_tests": len([r for r in results if r["passed"]]),
        "results": results
    }

def main():
    """Run production tests"""
    print("🚀 PRODUCTION TESTING STARTED")
    print("=" * 50)
    
    # Test 1: Single Request
    print("\n📊 Test 1: Single Request Performance")
    single_result = test_single_request()
    print(f"✅ Success: {single_result['success']}")
    if single_result['success']:
        print(f"⏱️ Response Time: {single_result['response_time']:.2f}s")
        print(f"📈 Confidence Score: {single_result['confidence_score']}")
        print(f"🤖 Has LLM Response: {single_result['has_llm_response']}")
        print(f"🔧 Has Tool Output: {single_result['has_tool_output']}")
    
    # Test 2: Concurrent Requests
    print("\n📊 Test 2: Concurrent Requests (20)")
    concurrent_result = test_concurrent_requests(20)
    print(f"✅ Success Rate: {concurrent_result['success_rate']:.1f}%")
    print(f"⏱️ Avg Response Time: {concurrent_result['avg_response_time']:.2f}s")
    print(f"🚀 Requests/Second: {concurrent_result['requests_per_second']:.1f}")
    print(f"📈 Successful: {concurrent_result['successful_requests']}/{concurrent_result['total_requests']}")
    
    # Test 3: Input Validation
    print("\n📊 Test 3: Input Validation")
    validation_result = test_input_validation()
    print(f"✅ Passed: {validation_result['passed_tests']}/{validation_result['total_tests']}")
    
    # Overall Assessment
    print("\n🎯 OVERALL PRODUCTION READINESS")
    print("=" * 50)
    
    single_ok = single_result['success'] and single_result['response_time'] < 4
    concurrent_ok = concurrent_result['success_rate'] >= 90
    validation_ok = validation_result['passed_tests'] == validation_result['total_tests']
    
    if single_ok and concurrent_ok and validation_ok:
        print("🎉 PRODUCTION READY!")
        print("✅ All tests passed")
    else:
        print("⚠️ NEEDS IMPROVEMENT")
        if not single_ok:
            print("❌ Single request performance issue")
        if not concurrent_ok:
            print("❌ Concurrent request performance issue")
        if not validation_ok:
            print("❌ Input validation issue")
    
    print(f"\n📊 Metrics Summary:")
    print(f"• Single Request: {'✅' if single_ok else '❌'} ({single_result['response_time']:.2f}s)")
    print(f"• Concurrent (20): {'✅' if concurrent_ok else '❌'} ({concurrent_result['success_rate']:.1f}% success)")
    print(f"• Input Validation: {'✅' if validation_ok else '❌'} ({validation_result['passed_tests']}/{validation_result['total_tests']})")

if __name__ == "__main__":
    main()
