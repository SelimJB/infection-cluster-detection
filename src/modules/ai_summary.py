import requests
import json


def generate_ai_summary(prompt, provider, model, api_key):
    """
    Generate AI summary using the specified provider and model

    Args:
        prompt: The formatted prompt to send to AI
        provider: "OpenAI (ChatGPT)" or "Anthropic (Claude)"
        model: Model name
        api_key: API key for the service

    Returns:
        dict: {"success": bool, "content": str, "error": str}
    """
    if not api_key:
        return {
            "success": False,
            "content": "",
            "error": "API key is required"
        }

    try:
        if provider == "OpenAI (ChatGPT)":
            return _call_openai(prompt, model, api_key)
        elif provider == "Anthropic (Claude)":
            return _call_anthropic(prompt, model, api_key)
        else:
            return {
                "success": False,
                "content": "",
                "error": f"Unsupported provider: {provider}"
            }
    except Exception as e:
        return {
            "success": False,
            "content": "",
            "error": f"API call failed: {str(e)}"
        }


def _call_openai(prompt, model, api_key):
    """Call OpenAI API"""
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return {
            "success": True,
            "content": content,
            "error": ""
        }
    else:
        error_msg = f"OpenAI API error {response.status_code}: {response.text}"
        return {
            "success": False,
            "content": "",
            "error": error_msg
        }


def _call_anthropic(prompt, model, api_key):
    """Call Anthropic Claude API"""
    url = "https://api.anthropic.com/v1/messages"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    data = {
        "model": model,
        "max_tokens": 1500,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        content = result["content"][0]["text"]
        return {
            "success": True,
            "content": content,
            "error": ""
        }
    else:
        error_msg = f"Anthropic API error {response.status_code}: {response.text}"
        return {
            "success": False,
            "content": "",
            "error": error_msg
        }


def generate_mock_summary(analysis_data):
    """
    Generate a mock AI summary for testing purposes

    Args:
        analysis_data: Analysis results data

    Returns:
        str: Mock summary
    """
    mock_summary = """
🤖 **AI ANALYSIS SUMMARY** (Mock Response)

**Key Findings:**
• Data contains multiple files with mixed numeric and text columns
• Statistical analysis shows varying data density across files
• Some columns contain missing values that may affect analysis quality

**Data Quality Assessment:**
• Files processed successfully with standard CSV parsing
• Numeric data available for quantitative analysis
• Text fields present for categorical analysis

**Infection Control Implications:**
• Data structure suggests comprehensive patient tracking system
• Multiple data sources indicate good documentation practices
• Missing values in certain fields may require data validation

**Recommendations:**
• Validate data completeness before final analysis
• Consider cross-referencing between microbiology and transfer data
• Implement data quality checks for future data collection

*Note: This is a mock analysis. Real analysis would provide specific epidemiological insights based on actual data patterns.*
"""
    return mock_summary
