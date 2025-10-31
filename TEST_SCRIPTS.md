# Load Testing Scripts

This directory contains scripts to test the Political Agent API under various conditions.

## Scripts

### 1. `test_quick.py` - Quick Manual Testing
Fast, readable test of a few queries. Good for development and debugging.

**Usage:**
```bash
python test_quick.py
```

**Output:**
- Displays full results for each query
- Shows summary, contradictions, and political parties
- Validates response completeness

---

### 2. `test_load.py` - Comprehensive Load Testing
Runs multiple iterations with detailed metrics tracking.

**Usage:**
```bash
# Default: 10 iterations per query, 1 concurrent request
python test_load.py

# Custom iterations
python test_load.py --iterations 20

# Test with concurrent requests
python test_load.py --iterations 10 --concurrent 3

# Heavy load test
python test_load.py --iterations 50 --concurrent 5
```

**Tracks:**
- ✅ Success rate
- ⚠️ Parsing errors
- ⚠️ Incomplete `political_parties` field
- ⏱️ Latency statistics (min, max, avg, median)
- 📊 Party count distribution
- 📝 Per-query success rates

**Output:**
- Console summary with statistics
- JSON file: `load_test_results_YYYYMMDD_HHMMSS.json`

---

## Test Queries

Both scripts test these topics:
1. Healthcare reform
2. Abortion legality
3. Climate change
4. Immigration policy
5. Government role in economy

---

## What to Look For

### ✅ Good Results
- `political_parties` contains all 3 parties: `["Conservative", "Liberal", "Socialist"]`
- `summary` is neutral and comprehensive
- `contradictions` highlights genuine policy conflicts
- Success rate > 95%

### ⚠️ Warning Signs
- `political_parties` is empty or has < 3 parties
- Parsing errors > 5%
- High latency (> 30s per request)
- Inconsistent results for the same query

### 🔍 Debugging
If you see issues:
1. Check logs for warnings about incomplete `political_parties`
2. Review the JSON output file for patterns
3. Look at the `errors` array in the summary
4. Compare results across multiple iterations of the same query

---

## Example Output

### Quick Test
```
================================================================================
Query: What is the best approach to healthcare reform?
================================================================================

✅ SUCCESS

--- Summary ---
Conservatives emphasize market-based solutions and reducing government 
intervention. Liberals advocate for universal coverage through government 
programs. Socialists support single-payer healthcare as a human right.

--- Contradictions ---
Conservatives oppose government expansion while Liberals and Socialists 
support increased government role in healthcare provision.

--- Political Parties ---
  • Conservative
  • Liberal
  • Socialist

--- Validation ---
  Party count: 3
  Summary length: 245 chars
  Has contradictions: Yes
```

### Load Test Summary
```
================================================================================
LOAD TEST SUMMARY
================================================================================
Total Requests: 50
Successful: 48 (96.0%)
Failed: 2 (4.0%)

⚠️  Incomplete political_parties: 3 (6.0%)

--- Latency Statistics ---
Min: 8.23s
Max: 15.67s
Avg: 11.45s
Median: 11.12s

--- Political Parties Distribution ---
3 parties: 47 times (94.0%)
2 parties: 2 times (4.0%)
0 parties: 1 times (2.0%)
```

---

## Tips

1. **Start with quick test**: Run `test_quick.py` first to verify basic functionality
2. **Gradual load increase**: Start with low iterations, then increase
3. **Monitor logs**: Keep an eye on the application logs while testing
4. **Rate limiting**: The scripts include delays to avoid overwhelming the API
5. **Save results**: Load test results are automatically saved with timestamps

---

## Troubleshooting

**Import errors:**
```bash
# Make sure you're in the project root
cd /Users/kennonyoung/Projects/political_agent

# Activate virtual environment if needed
source venv/bin/activate
```

**Environment variables:**
- Ensure `.env` file exists with required API keys
- Scripts automatically load `.env` via `python-dotenv`

**High failure rate:**
- Check if OpenAI API key is valid
- Verify network connectivity
- Review application logs for errors
