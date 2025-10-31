#!/usr/bin/env python3
"""
Load testing script for the Political Agent API.
Tests the mediator synthesis under various conditions and tracks:
- Success rate
- Parsing errors
- Incomplete political_parties
- Response consistency
- Latency
"""

import asyncio
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
import json
from dotenv import load_dotenv

from app.domain.orchestration.services.base_orchestration_service import OrchestratorAsync
from app.domain.agents.responses.mediator_response import MediatorResponse

# Load environment variables
load_dotenv()


class LoadTestResults:
    """Track and analyze load test results."""
    
    def __init__(self):
        self.total_requests = 0
        self.successful = 0
        self.failed = 0
        self.parsing_errors = 0
        self.incomplete_parties = 0
        self.latencies = []
        self.errors = []
        self.party_counts = defaultdict(int)
        self.results_by_query = defaultdict(list)
        
    def record_success(self, query: str, result: MediatorResponse, latency: float, expected_parties: int):
        self.total_requests += 1
        self.successful += 1
        self.latencies.append(latency)
        
        # Check if political_parties is complete
        actual_party_count = len(result.political_parties) if result.political_parties else 0
        if actual_party_count != expected_parties:
            self.incomplete_parties += 1
            
        self.party_counts[actual_party_count] += 1
        self.results_by_query[query].append({
            "success": True,
            "latency": latency,
            "parties": result.political_parties,
            "summary_length": len(result.summary),
            "has_contradictions": bool(result.contradictions)
        })
        
    def record_failure(self, query: str, error: Exception, latency: float):
        self.total_requests += 1
        self.failed += 1
        self.latencies.append(latency)
        self.errors.append(str(error))
        
        if "validation error" in str(error).lower() or "parsing" in str(error).lower():
            self.parsing_errors += 1
            
        self.results_by_query[query].append({
            "success": False,
            "latency": latency,
            "error": str(error)
        })
        
    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("LOAD TEST SUMMARY")
        print("="*80)
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nTotal Requests: {self.total_requests}")
        print(f"Successful: {self.successful} ({self.successful/self.total_requests*100:.1f}%)")
        print(f"Failed: {self.failed} ({self.failed/self.total_requests*100:.1f}%)")
        
        if self.parsing_errors > 0:
            print(f"\n⚠️  Parsing Errors: {self.parsing_errors} ({self.parsing_errors/self.total_requests*100:.1f}%)")
            
        if self.incomplete_parties > 0:
            print(f"⚠️  Incomplete political_parties: {self.incomplete_parties} ({self.incomplete_parties/self.total_requests*100:.1f}%)")
            
        print(f"\n--- Latency Statistics ---")
        if self.latencies:
            print(f"Min: {min(self.latencies):.2f}s")
            print(f"Max: {max(self.latencies):.2f}s")
            print(f"Avg: {sum(self.latencies)/len(self.latencies):.2f}s")
            print(f"Median: {sorted(self.latencies)[len(self.latencies)//2]:.2f}s")
            
        print(f"\n--- Political Parties Distribution ---")
        for count, occurrences in sorted(self.party_counts.items()):
            print(f"{count} parties: {occurrences} times ({occurrences/self.total_requests*100:.1f}%)")
            
        if self.errors:
            print(f"\n--- Error Samples (first 5) ---")
            for i, error in enumerate(self.errors[:5], 1):
                print(f"{i}. {error[:200]}...")
                
        print("\n--- Results by Query ---")
        for query, results in self.results_by_query.items():
            success_count = sum(1 for r in results if r.get("success"))
            print(f"\nQuery: '{query[:60]}...'")
            print(f"  Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
            if success_count > 0:
                avg_latency = sum(r["latency"] for r in results if r.get("success")) / success_count
                print(f"  Avg latency: {avg_latency:.2f}s")
                
        print("\n" + "="*80)


async def test_single_query(orchestrator: OrchestratorAsync, query: str, expected_parties: int = 3) -> tuple:
    """Test a single query and return (success, result_or_error, latency)."""
    start_time = time.time()
    try:
        result = await orchestrator.route_and_execute(query)
        latency = time.time() - start_time
        return (True, result, latency)
    except Exception as e:
        latency = time.time() - start_time
        return (False, e, latency)


async def run_load_test(num_iterations: int = 10, concurrent_requests: int = 1):
    """
    Run load test with specified parameters.
    
    Args:
        num_iterations: Number of times to run each test query
        concurrent_requests: Number of concurrent requests per iteration
    """
    results = LoadTestResults()
    
    # Test queries covering different topics
    test_queries = [
        "What is the best approach to healthcare reform?",
        "Should abortion be legal?",
        "What should be done about climate change?",
        "How should we handle immigration policy?",
        "What is the role of government in the economy?",
    ]
    
    print(f"\n{'='*80}")
    print(f"Starting Load Test")
    print(f"{'='*80}")
    print(f"Iterations per query: {num_iterations}")
    print(f"Concurrent requests: {concurrent_requests}")
    print(f"Total queries: {len(test_queries)}")
    print(f"Total requests: {len(test_queries) * num_iterations * concurrent_requests}")
    print(f"{'='*80}\n")
    
    for iteration in range(num_iterations):
        print(f"\n--- Iteration {iteration + 1}/{num_iterations} ---")
        
        for query_idx, query in enumerate(test_queries, 1):
            print(f"  Testing query {query_idx}/{len(test_queries)}: '{query[:50]}...'", end=" ")
            
            # Create tasks for concurrent requests
            tasks = []
            for _ in range(concurrent_requests):
                orchestrator = OrchestratorAsync()
                tasks.append(test_single_query(orchestrator, query, expected_parties=3))
            
            # Run concurrently
            responses = await asyncio.gather(*tasks)
            
            # Process results
            for success, result_or_error, latency in responses:
                if success:
                    results.record_success(query, result_or_error, latency, expected_parties=3)
                    print("✓", end="")
                else:
                    results.record_failure(query, result_or_error, latency)
                    print("✗", end="")
            
            print(f" ({latency:.2f}s)")
            
            # Small delay between queries to avoid rate limiting
            await asyncio.sleep(0.5)
    
    # Print summary
    results.print_summary()
    
    # Save detailed results to file
    save_results_to_file(results)
    
    return results


def save_results_to_file(results: LoadTestResults):
    """Save detailed results to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"load_test_results_{timestamp}.json"
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_requests": results.total_requests,
            "successful": results.successful,
            "failed": results.failed,
            "parsing_errors": results.parsing_errors,
            "incomplete_parties": results.incomplete_parties,
            "success_rate": results.successful / results.total_requests if results.total_requests > 0 else 0,
        },
        "latency_stats": {
            "min": min(results.latencies) if results.latencies else 0,
            "max": max(results.latencies) if results.latencies else 0,
            "avg": sum(results.latencies) / len(results.latencies) if results.latencies else 0,
            "median": sorted(results.latencies)[len(results.latencies)//2] if results.latencies else 0,
        },
        "party_distribution": dict(results.party_counts),
        "errors": results.errors,
        "results_by_query": {k: v for k, v in results.results_by_query.items()},
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {filename}")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load test the Political Agent API")
    parser.add_argument(
        "--iterations", 
        type=int, 
        default=10,
        help="Number of iterations per query (default: 10)"
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=1,
        help="Number of concurrent requests per iteration (default: 1)"
    )
    
    args = parser.parse_args()
    
    await run_load_test(
        num_iterations=args.iterations,
        concurrent_requests=args.concurrent
    )


if __name__ == "__main__":
    asyncio.run(main())
