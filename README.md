# MRFR - Market Research Fact Review

A Python-based tool for analyzing market research documents and performing fact-checking and relevance/grammar validation using OpenAI's API.

## Features

- **Fact Checking**: Validates factual claims in market research documents
- **Relevance & Grammar Check**: Ensures content relevance and grammatical correctness
- **Cost Tracking**: Monitors API usage costs
- **JSON Processing**: Handles structured data input/output
- **Modular Design**: Separated concerns for easy maintenance

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- pip or uv package manager

## Installation

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd mrfr-test
   ```

2. **Install dependencies**:
   
   Using pip:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using uv (recommended):
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```env
   api_key=your_openai_api_key_here
   ```

## Project Structure

```
mrfr-test/
├── main.py                 # Main execution script
├── functions.py            # Core analysis functions
├── prompts.py              # System prompts and templates
├── cost_tracker.py         # API cost tracking
├── json_utils.py           # JSON file utilities
├── prompts.json            # Prompt configurations
├── contexts/               # Input market research documents
│   ├── false_Airborne_Wind_Energy_Market.json
│   ├── final_context_Airborne_Wind_Energy_Market.json
│   └── ...
├── output/                 # Generated results
└── README.md
```

## Usage

### Running the Main Script

1. **Ensure your environment is set up**:
   - Verify your `.env` file contains the API key
   - Make sure all dependencies are installed

2. **Run the analysis**:
   ```bash
   python main.py
   ```

3. **Check the output**:
   - Results will be saved to `output_final.json`
   - Cost and timing information will be displayed in the console

### Input Files

- **`prompts.json`**: Contains prompt configurations for different analysis types
- **`contexts/false_Airborne_Wind_Energy_Market.json`**: Sample market research document to analyze

### Output

The script generates:
- **`output_final.json`**: Detailed analysis results including:
  - Relevance and grammar check results
  - Fact-checking results
  - Error handling for failed analyses
- **Console output**: Total execution time and API costs

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `api_key` | Your OpenAI API key | Yes |

### Customizing Analysis

You can modify the analysis by:
1. **Adding new sections** to `prompts.json`
2. **Updating prompts** in the prompt configurations
3. **Changing input files** in the `contexts/` directory

## Dependencies

Key dependencies include:
- `openai`: OpenAI API client
- `python-dotenv`: Environment variable management
- `json`: JSON processing (built-in)
- `logging`: Logging functionality (built-in)

## Cost Tracking

The application automatically tracks API usage costs and displays:
- Total cost for the session
- Cost breakdown by API call
- Cost details in the console output
