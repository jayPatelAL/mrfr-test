import logging
import json
from openai import OpenAI
from prompts import sys_prompt, grammar_sys_prompt
from openai_cost_calculator import estimate_cost
import time
import re
class Analyzer:
    def __init__(self, api_key, cost_tracker):
        self.client = OpenAI(api_key=api_key)
        self.cost_tracker = cost_tracker
    
    def run_hallucination_check(self,system_prompt, user_prompt, model="gpt-4o-mini", temperature=0, response_format={"type": "json_object"}):
        start_time = time.time()
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            response_format=response_format
        )
        end_time = time.time()
        duration = end_time - start_time

        cost_details = estimate_cost(response)
        total_cost = float(cost_details["total_cost"])
        
        print(f"Chat Completion - Duration: {duration:.2f}s, Cost: ${total_cost:.6f}, Model: {model}")
        
        # Add to tracker with duration info
        cost_details["duration_seconds"] = round(duration, 2)
        self.cost_tracker.add(total_cost, cost_details)
        return response
    
    def run_fact_check(self,user_prompt,description, model="gpt-4o-mini"):
        start_time = time.time()
        full_prompt = f"{user_prompt}\n\n{description}"
        # print(f"!!!!!!!!the prompt:\n {full_prompt}")
        try:
            response = self.client.responses.create(
                model=model,
                tools=[{"type": "web_search_preview"}],
                input=full_prompt
            )
            end_time = time.time()
            duration = end_time - start_time

            if hasattr(response, 'usage') and response.usage:
                cost_details = estimate_cost(response)
                total_cost = float(cost_details["total_cost"])
                cost_details["duration_seconds"] = round(duration, 2)
                self.cost_tracker.add(total_cost, cost_details)
            else:
                # Fallback estimation for fact-checking
                estimated_cost = 0.01
                cost_details = {
                    "model": model,
                    "estimated": True,
                    "total_cost": estimated_cost,
                    "duration_seconds": round(duration, 2)
                }
                self.cost_tracker.add(estimated_cost, cost_details)
                total_cost = estimated_cost
            
            print(f"Fact Check - Duration: {duration:.2f}s, Cost: ${total_cost:.6f}, Model: {model}")

            return response
        except Exception as e:
            print(f"Error in fact-checking {e}")
            return None
        
    def extract_json_from_response(self,response_text):
        """Extract and parse JSON content from AI response, handling markdown code blocks"""
        try:
            json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx + 1]
                else:
                    json_str = response_text
            
            # Parse the JSON
            parsed_json = json.loads(json_str)
            return parsed_json
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON: {e}")
            logging.error(f"Raw response: {response_text}")
            return {"error": "Failed to parse response", "raw_response": response_text}
        except Exception as e:
            logging.error(f"Error extracting JSON: {e}")
            return {"error": str(e), "raw_response": response_text}
