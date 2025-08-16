from enum import Enum


class AnalysisType(Enum):
    """Enumeration of available analysis types"""
    STANDARD = "standard"
    MOCK = "mock"

    @property
    def display_name(self):
        """Get user-friendly display name"""
        names = {
            self.STANDARD: "🧬 Episode-Based Cluster Detection",
            self.MOCK: "🧪 Mock Analysis",
        }
        return names[self]

    @property
    def description(self):
        """Get detailed description"""
        descriptions = {
            self.STANDARD: "Advanced infection cluster detection using episode-based graph analysis",
            self.MOCK: "Mock data analysis for testing and development purposes",
        }
        return descriptions[self]


def run_analysis_workflow(micro_data, transfer_data, analysis_type=AnalysisType.STANDARD):
    """
    Execute complete analysis workflow on microbiology and transfer data

    Args:
        micro_data: List of microbiology data entries
        transfer_data: List of transfer data entries
        analysis_type: AnalysisType enum (default: AnalysisType.STANDARD)

    Returns:
        dict: {
            "success": bool,
            "message": str,
            "raw_results": dict,
            "analysis_results": dict,
            "formatted_results": str,
            "analysis_type": str
        }
    """
    try:
        if not micro_data or not transfer_data:
            return {
                "success": False,
                "message": "Both Microbiology and Transfers data are required",
                "analysis_results": None,
                "formatted_results": None,
                "analysis_type": analysis_type
            }

        analysis_results, formatted_results = _run_analysis_by_type(
            micro_data, transfer_data, analysis_type)

        return {
            "success": True,
            "message": f"Analysis completed successfully using {analysis_type.display_name}!",
            "raw_results": analysis_results,
            "analysis_results": analysis_results,
            "formatted_results": formatted_results,
            "analysis_type": analysis_type
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Analysis failed: {str(e)}",
            "raw_results": None,
            "analysis_results": None,
            "formatted_results": None,
            "analysis_type": analysis_type
        }


def _run_analysis_by_type(micro_data, transfer_data, analysis_type):
    """
    Run analysis based on the specified type

    Args:
        micro_data: List of microbiology data entries
        transfer_data: List of transfer data entries
        analysis_type: AnalysisType enum

    Returns:
        tuple: (analysis_results, formatted_results)
    """
    if analysis_type == AnalysisType.MOCK:
        from .mock_data_analysis import analyze_csv_data, format_analysis_results
    elif analysis_type == AnalysisType.STANDARD:
        from .data_analysis import analyze_csv_data, format_analysis_results
    else:
        from .data_analysis import analyze_csv_data, format_analysis_results

    # Prepare data in the format expected by analyze_csv_data
    all_data = []
    for data in micro_data:
        all_data.append({
            "filename": f"microbiology_{data.get('filename', 'unknown')}",
            "content": data.get('content', '')
        })

    for data in transfer_data:
        all_data.append({
            "filename": f"transfers_{data.get('filename', 'unknown')}",
            "content": data.get('content', '')
        })

    analysis_results = analyze_csv_data(all_data)
    formatted_results = format_analysis_results(analysis_results)

    return analysis_results, formatted_results
