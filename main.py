import logging
import os
import re
from dotenv import load_dotenv
from json_utils import load_json, save_json, extract_sections
from openai_cost_calculator import estimate_cost
from cost_tracker import CostTracker
from functions import Analyzer
from prompts import unified_prompt
import json
import time

def load_config():
    load_dotenv()
    return {
        "api_key": os.getenv("api_key"),
    }

def extract_number_from_filename(filename):
    # Extract number from filenames like market_*_874.json
    match = re.search(r'market_\w+_(\d+)', filename)
    if match:
        return match.group(1)
    return ""

def process_files(input_dir, file_type, prompts, analyzer, cost_tracker):
    logging.info(f"Processing {file_type} files from: {input_dir}")
    
    if not os.path.exists(input_dir):
        logging.error(f"Directory not found: {input_dir}")
        return []
    
    # Updated file pattern to handle both "trends" and "shares"
    file_prefix = "market_trends_" if file_type == "trend" else "market_share_"
    
    # List all market analysis files
    input_files = [f for f in os.listdir(input_dir) 
                  if f.startswith(file_prefix) and f.endswith(".json")]
    
    if not input_files:
        logging.error(f"No {file_type} files found in {input_dir}")
        return []
        
    logging.info(f"Found {len(input_files)} {file_type} files to process")
    
    # Sort files by their number
    input_files.sort(key=lambda x: int(extract_number_from_filename(x)))
    
    processed_files = []
    for input_file in input_files:
        full_path = os.path.join(input_dir, input_file)
        logging.info(f"Processing {file_type} file: {input_file}")
        try:
            with open(full_path, "r", encoding='utf-8') as f:
                main = json.load(f)
            
            results = {}
            
            # Process appropriate section based on file type
            section_to_process = "top_trends" if file_type == "trend" else "competitive_positioning"
            if section_to_process in main:
                section_result = {}
                analysis_data = main[section_to_process]
                
                # For relevance and grammar check
                try:
                    user_prompt = f"{prompts['marketDrivers']['relevanceGrammarCheck'].strip()}\n\nHere is the section data:\n{json.dumps(analysis_data, indent=2)}"
                    response = analyzer.run_hallucination_check(
                        system_prompt=unified_prompt,
                        user_prompt=user_prompt
                    )
                    result_text = response.choices[0].message.content
                    parsed_rg_json = analyzer.extract_json_from_response(result_text)
                    
                    cost_details = estimate_cost(response)
                    cost_tracker.add(float(cost_details["total_cost"]), cost_details)
                    section_result["relevanceGrammarCheck"] = parsed_rg_json
                except Exception as e:
                    section_result["relevanceGrammarCheck"] = {"error": str(e), "status": "failed"}
                
                # For fact check
                try:
                    prompt = prompts['marketDrivers']['factCheck']
                    response_ws = analyzer.run_fact_check(user_prompt=prompt, description=analysis_data)
                    result_text_ws = response_ws.output_text
                    parsed_fc_json = analyzer.extract_json_from_response(result_text_ws)
                    from openai_cost_calculator import estimate_cost
                    cost_details = estimate_cost(response_ws)
                    cost_tracker.add(float(cost_details["total_cost"]), cost_details)
                    section_result["factCheck"] = parsed_fc_json
                except Exception as e:
                    section_result["factCheck"] = {"error": str(e), "status": "failed"}
                
                results[section_to_process] = section_result
            
            # Save results in appropriate output directory
            file_number = extract_number_from_filename(input_file)
            output_dir = f"output_{file_type}s"  # Added 's' to make it plural
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"output_{file_type}_{file_number}.json")
            
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            processed_files.append({
                'type': file_type,
                'input': input_file,
                'output': os.path.basename(output_file),
                'status': 'success'
            })
            
            logging.info(f"Results saved to {output_file}")
            
        except Exception as e:
            logging.error(f"Error processing {input_file}: {str(e)}")
            processed_files.append({
                'type': file_type,
                'input': input_file,
                'status': 'failed',
                'error': str(e)
            })
    
    return processed_files

def main():
    total_start = time.time()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config = load_config()
    cost_tracker = CostTracker()
    analyzer = Analyzer(config["api_key"], cost_tracker)
    
    logging.info("Starting analysis...")
    
    with open("prompts.json", "r", encoding='utf-8') as f:
        prompts = json.load(f)
    
    # Process both Trends and Shares folders
    all_processed_files = []
    
    # Process Shares
    shares_dir = os.path.join("contexts", "Shares")
    share_results = process_files(shares_dir, "share", prompts, analyzer, cost_tracker)
    all_processed_files.extend(share_results)
    
    # Process Trends
    trends_dir = os.path.join("contexts", "Trends")
    trend_results = process_files(trends_dir, "trend", prompts, analyzer, cost_tracker)
    all_processed_files.extend(trend_results)
    
    # Save processing summary
    summary_file = os.path.join("output", "processing_summary.json")
    os.makedirs("output", exist_ok=True)
    
    with open(summary_file, "w", encoding='utf-8') as f:
        json.dump({
            'total_files': len(all_processed_files),
            'shares_processed': len(share_results),
            'trends_processed': len(trend_results),
            'processed_files': all_processed_files,
            'total_cost': cost_tracker.total_cost
        }, f, indent=2, ensure_ascii=False)
    
    total_end = time.time()
    total_duration = total_end - total_start
    
    print(f"\nProcessing Summary:")
    print(f"Total Files Processed: {len(all_processed_files)}")
    print(f"- Share Files: {len(share_results)}")
    print(f"- Trend Files: {len(trend_results)}")
    print(f"Total Time: {total_duration:.2f} seconds")
    print(f"Total Cost: ${cost_tracker.total_cost:.6f}")
    print(f"Detailed summary saved to: {summary_file}")

if __name__ == "__main__":
    main()