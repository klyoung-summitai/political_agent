#!/usr/bin/env python3
"""
Quick test script for the Political Agent API.
Runs a few test queries and displays results in a readable format.
"""

import asyncio
from dotenv import load_dotenv
from app.domain.orchestration.services.base_orchestration_service import OrchestratorAsync

# Load environment variables
load_dotenv()


async def test_query(query: str):
    """Test a single query and print results."""
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    orchestrator = OrchestratorAsync()
    
    try:
        result = await orchestrator.route_and_execute(query)
        
        print(f"\n✅ SUCCESS")
        print(f"\n--- Summary ---")
        print(result.summary)
        
        print(f"\n--- Contradictions ---")
        print(result.contradictions if result.contradictions else "(None)")
        
        print(f"\n--- Political Parties ---")
        if result.political_parties:
            for party in result.political_parties:
                print(f"  • {party}")
        else:
            print("  ⚠️  No parties listed!")
            
        print(f"\n--- Validation ---")
        print(f"  Party count: {len(result.political_parties) if result.political_parties else 0}")
        print(f"  Summary length: {len(result.summary)} chars")
        print(f"  Has contradictions: {'Yes' if result.contradictions else 'No'}")
        
    except Exception as e:
        print(f"\n❌ FAILED")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run quick tests."""
    test_queries = [
        "What is the best approach to healthcare reform?",
        "Should abortion be legal?",
        "What should be done about climate change?",
    ]
    
    print("\n" + "="*80)
    print("QUICK TEST - Political Agent API")
    print("="*80)
    print(f"Running {len(test_queries)} test queries...")
    
    for query in test_queries:
        await test_query(query)
        await asyncio.sleep(1)  # Brief pause between queries
    
    print("\n" + "="*80)
    print("TESTS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
