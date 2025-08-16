from .data_analysis import analyze_csv_data, format_analysis_results


def run_analysis_workflow(micro_data, transfer_data):
    """
    Execute complete analysis workflow on microbiology and transfer data

    Args:
        micro_data: List of microbiology data entries
        transfer_data: List of transfer data entries

    Returns:
        dict: {
            "success": bool,
            "message": str,
            "analysis_results": dict,
            "formatted_results": str
        }
    """
    try:
        if not micro_data or not transfer_data:
            return {
                "success": False,
                "message": "Both Microbiology and Transfers data are required",
                "analysis_results": None,
                "formatted_results": None
            }

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

        return {
            "success": True,
            "message": "Analysis completed successfully!",
            "analysis_results": analysis_results,
            "formatted_results": formatted_results
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Analysis failed: {str(e)}",
            "analysis_results": None,
            "formatted_results": None
        }
