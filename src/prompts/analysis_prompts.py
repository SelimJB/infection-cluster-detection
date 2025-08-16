"""
Prompts for AI analysis of infection cluster data
"""

# Base prompt template for summarizing analysis results
ANALYSIS_SUMMARY_PROMPT = """
You are a medical data analyst specializing in infection cluster analysis. 

You have been provided with statistical analysis results from microbiology and patient transfer data. 
Your task is to summarize these findings in a clear, professional manner that would be useful for healthcare professionals.

ANALYSIS DATA:
{analysis_results}

Please provide a concise summary that includes:
1. Key statistics and trends identified
2. Notable patterns in the data
3. Potential implications for infection control
4. Any data quality concerns or limitations

Keep your response focused, professional, and actionable. Use bullet points where appropriate for clarity.
"""

# Alternative prompt for different analysis types
DETAILED_ANALYSIS_PROMPT = """
As an infectious disease epidemiologist, please analyze the following data summary from a hospital infection cluster investigation:

DATA SUMMARY:
{analysis_results}

Provide a detailed analysis covering:

**Data Overview:**
- Summarize the scope and quality of the data

**Key Findings:**
- Highlight the most significant statistical findings
- Identify any patterns that merit attention

**Epidemiological Considerations:**
- Discuss potential transmission patterns
- Comment on data completeness and reliability

**Recommendations:**
- Suggest next steps for the investigation
- Recommend additional data collection if needed

Please structure your response clearly and focus on actionable insights.
"""

# Simple prompt for quick summaries
QUICK_SUMMARY_PROMPT = """
Summarize these infection cluster data analysis results in 3-4 bullet points:

{analysis_results}

Focus on the most important findings and any concerns that need immediate attention.
"""


def get_prompt_template(prompt_type="standard"):
    """
    Get the appropriate prompt template

    Args:
        prompt_type: Type of prompt ("standard", "detailed", "quick")

    Returns:
        str: Prompt template
    """
    prompt_templates = {
        "standard": ANALYSIS_SUMMARY_PROMPT,
        "detailed": DETAILED_ANALYSIS_PROMPT,
        "quick": QUICK_SUMMARY_PROMPT
    }

    return prompt_templates.get(prompt_type, ANALYSIS_SUMMARY_PROMPT)


def format_prompt(analysis_results, prompt_type="standard"):
    """
    Format the prompt with analysis results

    Args:
        analysis_results: String or dict containing analysis results
        prompt_type: Type of prompt to use

    Returns:
        str: Formatted prompt ready for AI
    """
    template = get_prompt_template(prompt_type)

    if isinstance(analysis_results, dict):
        analysis_results = str(analysis_results)

    return template.format(analysis_results=analysis_results)
