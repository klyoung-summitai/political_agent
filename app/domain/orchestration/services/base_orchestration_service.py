import sys
import json
import asyncio
import time
import uuid
from loguru import logger
from pydantic import BaseModel, ValidationError
from prometheus_client import Summary, start_http_server
from langchain_core.output_parsers import PydanticOutputParser
from app.domain.agents.entities.mediator_agent import MediatorAgent
from app.domain.agents.responses.mediator_response import MediatorResponse

# ----------------------------
# Metrics
# ----------------------------
AGENT_LATENCY = Summary("agent_latency_seconds", "Latency per agent call", ["agent"])

# Start Prometheus metrics server on port 8001
start_http_server(8001)

# ----------------------------
# Response validation schema
# ----------------------------
class AgentResponse(BaseModel):
    content: str  # or more structured fields if your agents return structured JSON
    # Add more fields as needed

# ----------------------------
# Orchestrator
# ----------------------------
class OrchestratorAsync:
    def __init__(self):
        self.orchestration_agent = MediatorAgent()
    
    @staticmethod
    def _strip_markdown_json(content: str) -> str:
        """
        Strip markdown code block wrappers from JSON content.
        Handles formats like: ```json\n{...}\n``` or ```\n{...}\n```
        """
        import re
        # Remove ```json or ``` at start and ``` at end
        content = content.strip()
        # Pattern: optional ```json or ```, then content, then optional ```
        pattern = r'^```(?:json)?\s*\n?(.*?)\n?```$'
        match = re.match(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return content
    
    async def _invoke_llm(self, user_query: str):
        """
        Wrap the blocking mediator.execute() call in a thread executor for async usage.
        """
        loop = asyncio.get_event_loop()
        trace_id = str(uuid.uuid4())
       ## logger.info(f"[{trace_id}] Invoking mediator for query: {user_query}")
        start_time = time.time()
        response = await loop.run_in_executor(None, self.orchestration_agent.execute, user_query)
        duration = time.time() - start_time
       ## logger.info(f"[{trace_id}] Mediator responded in {duration:.2f}s: {response}")
        return response, trace_id

    async def _call_agent(self, agent, query: str, trace_id: str):
        """
        Wrap the agent's execute method to run asynchronously with logging, metrics, and validation.
        """
        start_time = time.time()
        ##logger.info(f"[{trace_id}] Calling agent: {agent.name} for query: {query}")
        try:
            loop = asyncio.get_event_loop()
            raw_response = await loop.run_in_executor(None, agent.execute, query)
            duration = time.time() - start_time

            # Metrics
            AGENT_LATENCY.labels(agent=agent.name).observe(duration)

            # Validate response
            try:
                response = raw_response
            except ValidationError as ve:
                logger.warning(f"[{trace_id}] Agent {agent.name} returned invalid output: {ve}")
                response = raw_response  # fallback to raw

            logger.info(f"[{trace_id}] Agent {agent.name} responded in {duration:.2f}s: {response}")
            return response.dict()

        except Exception as e:
            ##logger.exception(f"[{trace_id}] Error calling agent {agent.name}: {e}")
            return {"error": str(e)}

    async def route_and_execute(self, user_query: str) -> dict:
        response, trace_id = await self._invoke_llm(user_query)

        # Determine which agents to call
        try:
            logger.info(f"mediator ky response {response}")
            agents_to_invoke = json.loads(response)["agents_to_invoke"]
        except Exception:
          ##  logger.warning(f"[{trace_id}] Failed to parse mediator response, calling all agents")
            agents_to_invoke = list(self.orchestration_agent.get_available_agents().keys())

        # Execute agents concurrently
        tasks = [
            self._call_agent(self.orchestration_agent.get_available_agents()[name], user_query, trace_id)
            for name in agents_to_invoke
        ]

        sub_agent_responses = await asyncio.gather(*tasks)
        
        # Filter out errors and format responses
        valid_responses = []
        for resp in sub_agent_responses:
            if isinstance(resp, dict):
                if 'error' in resp:
                    logger.warning(f"[{trace_id}] Skipping error response: {resp['error']}")
                    continue
                if 'party' in resp and 'content' in resp:
                    valid_responses.append(resp)
                else:
                    logger.warning(f"[{trace_id}] Response missing party or content: {resp}")
        
        if not valid_responses:
            logger.error(f"[{trace_id}] No valid agent responses received")
            raise ValueError("No valid responses from political agents")
        
        sub_agent_text = "\n\n".join(
            [f"{resp['party']}: {resp['content']}" for resp in valid_responses]
        )

        ##logger.info(f"sub_agent_respones {sub_agent_text}")

        ##results = dict(zip(agents_to_invoke, results_list))
        prompt, parser = self.orchestration_agent.get_synthesize_prompt()
        
        input_data = {
            "query": user_query,
            "sub_agent_responses": sub_agent_text
        }

        # Extract actual parties that responded (from valid responses only)
        actual_parties = [resp['party'] for resp in valid_responses]
        logger.info(f"[{trace_id}] Actual parties that responded: {actual_parties}")
        
        chain = prompt | self.orchestration_agent.llm | parser
        
        try:
            results = chain.invoke(input_data)
            
            # Validate that political_parties matches actual responding agents
            if not results.political_parties or len(results.political_parties) != len(actual_parties):
                logger.warning(
                    f"[{trace_id}] LLM returned incomplete political_parties: {results.political_parties}. "
                    f"Expected: {actual_parties}. Correcting..."
                )
                results.political_parties = actual_parties
                
        except Exception as e:
            logger.warning(f"[{trace_id}] Parser failed: {e}. Attempting fallback parsing.")
            
            # Try to get raw LLM output without parser
            raw_chain = prompt | self.orchestration_agent.llm
            raw_output = raw_chain.invoke(input_data)
            
            # Strip markdown code blocks if present
            content = raw_output.content if hasattr(raw_output, 'content') else str(raw_output)
            content = self._strip_markdown_json(content)
            
            # Attempt to parse as JSON and add missing field
            try:
                import json
                parsed_dict = json.loads(content)
                if 'political_parties' not in parsed_dict:
                    parsed_dict['political_parties'] = actual_parties
                results = MediatorResponse(**parsed_dict)
            except Exception as parse_error:
                logger.error(f"[{trace_id}] Failed to parse even after stripping markdown: {parse_error}")
                # Last resort: return a minimal valid response
                results = MediatorResponse(
                    summary=content,
                    contradictions="",
                    political_parties=actual_parties
                )
    

        ##logger.info(f"[{trace_id}] Completed all agent calls for query: {user_query}")
        ##logger.info(f"final response {results}")
        return results
