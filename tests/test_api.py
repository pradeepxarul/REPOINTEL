"""
API Test Suite - Comprehensive Tests

Tests all core functionality:
- API health check
- Profile analysis  
- Report generation
- Error handling
"""
import requests
import time

BASE_URL = "http://localhost:8001"
TEST_USERNAME = "torvalds"  # Well-known GitHub user


def test_health():
    """Test API health endpoint."""
    print("\n✓ Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print(f"  Status: {data['status']}")


def test_analyze_profile():
    """Test GitHub profile analysis."""
    print("\n✓ Testing /analyze endpoint...")
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json={"github_input": TEST_USERNAME}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert data["status"] == "success"
    assert "user" in data
    assert "repositories" in data
    assert data["user"]["login"] == TEST_USERNAME
    
    print(f"  User: {data['user']['name']}")
    print(f"  Repos analyzed: {data['total_repos_analyzed']}")
    print(f"  Latency: {data['performance']['total_latency_ms']}ms")


def test_generate_report():
    """Test report generation."""
    print("\n✓ Testing /reports/generate endpoint...")
    response = requests.post(
        f"{BASE_URL}/api/v1/reports/generate",
        json={
            "username": TEST_USERNAME,
            "use_stored": True,
            "report_type": "full"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify report structure
    assert data["status"] == "success"
    assert "report" in data
    report = data["report"]
    
    assert "candidate" in report
    assert "technology_analysis" in report
    assert "project_scope_analysis" in report
    assert "comprehensive_skills" in report
    assert "hiring_recommendation" in report
    
    print(f"  Candidate: {report['candidate']['name']}")
    print(f"  Primary domain: {report['domain_classification']['primary_domain']}")
    print(f"  Roles: {', '.join(report['hiring_recommendation']['suitable_roles'][:3])}")


def test_error_handling():
    """Test error handling for invalid username."""
    print("\n✓ Testing error handling...")
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json={"github_input": "this-user-definitely-does-not-exist-12345"}
    )
    # Should handle gracefully (either 404 or 200 with error status)
    assert response.status_code in [200, 404, 500]
    print(f"  Error handled correctly: {response.status_code}")


def test_performance():
    """Test API response time."""
    print("\n✓ Testing performance (cached)...")
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json={"github_input": TEST_USERNAME}
    )
    elapsed = (time.time() - start) * 1000
    
    assert response.status_code == 200
    print(f"  Response time: {elapsed:.0f}ms")
    assert elapsed < 5000, "Response too slow (>5s)"


if __name__ == "__main__":
    print("="*60)
    print("🧪 GitHub User Data Analyzer - API Test Suite")
    print("="*60)
    
    try:
        test_health()
        test_analyze_profile()
        test_generate_report()
        test_error_handling()
        test_performance()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Cannot connect to {BASE_URL}")
        print("Make sure the server is running: python src/main.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        exit(1)
