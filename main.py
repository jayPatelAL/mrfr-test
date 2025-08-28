import logging
import os
from dotenv import load_dotenv
from json_utils import load_json, save_json, extract_sections
from cost_tracker import CostTracker
from functions import Analyzer
from prompts import unified_prompt
import json
import time

def load_config():
    load_dotenv()
    return {
        "api_key": os.getenv("api_key"),
        # "input_path": os.getenv("INPUT_PATH", r"C:\Users\jaysu\Desktop\AtomicLoopsIntern\mrfr\contexts\test_ip.json"),
        # "output_path": os.getenv("OUTPUT_PATH", r"C:\Users\jaysu\Desktop\AtomicLoopsIntern\mrfr\output\test2_result.json"),
    }
def main():
    total_start = time.time()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config = load_config()
    cost_tracker = CostTracker()
    analyzer = Analyzer(config["api_key"], cost_tracker)

    logging.info("Starting analysis...")


    with open("prompts.json", "r") as f:
        prompts = json.load(f)

    with open("contexts/false_Airborne_Wind_Energy_Market.json", "r") as f:
        main = json.load(f)

    results = {}

    for section, prompt_group in prompts.items():
        section_result = {}

        if section in main and "relevanceGrammarCheck" in prompt_group:
            prompt = prompt_group["relevanceGrammarCheck"]
            section_data = main[section]
            section_json = json.dumps(section_data, indent=2)
            user_prompt = f"{prompt.strip()}\n\nHere is the section data:\n{section_json}"
            try:
                response = analyzer.run_hallucination_check(
                    system_prompt=unified_prompt,
                    user_prompt=user_prompt
                )
                result_text = response.choices[0].message.content
                # logging.info(f"result text for {section}.....{result_text}")
                parsed_rg_json = analyzer.extract_json_from_response(result_text)
                # Calculate and add cost for run_chat_completion
                from openai_cost_calculator import estimate_cost
                cost_details = estimate_cost(response)
                cost_tracker.add(float(cost_details["total_cost"]), cost_details)
            except Exception as e:
                result_text = f"ERROR: {e}"
                parsed_rg_json = {"error": str(e), "status": "failed"}
            section_result["relevanceGrammarCheck"] = parsed_rg_json

        if section in main and "factCheck" in prompt_group:
            prompt = prompt_group["factCheck"]   
            section_data = main[section]
            try:
                response_ws = analyzer.run_fact_check(user_prompt=prompt, description=section_data)
                result_text_ws = response_ws.output_text
                # logging.info(f"Fact check response for {section}\n\n{result_text_ws}")
                parsed_fc_json = analyzer.extract_json_from_response(result_text_ws)
                # Calculate and add cost for run_fact_check
                from openai_cost_calculator import estimate_cost
                cost_details = estimate_cost(response_ws)
                cost_tracker.add(float(cost_details["total_cost"]), cost_details)
            except Exception as e:
                result_text_ws = f"Error {e}"
                parsed_fc_json = {"error": str(e), "status":"False"}
            section_result["factCheck"] = parsed_fc_json

        if section_result:
            results[section] = section_result


    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results to output directory
    output_file = os.path.join(output_dir, "output_final.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    logging.info(f"Results saved to {output_file}")
    total_end = time.time()
    total_duration = total_end - total_start

    print(f"Total Time: {total_duration:.2f} seconds")
    print(f"Total Cost: ${cost_tracker.total_cost:.6f}")
    
    
if __name__ == "__main__":
    main()