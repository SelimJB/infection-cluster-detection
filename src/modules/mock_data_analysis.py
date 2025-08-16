import pandas as pd
from io import StringIO
import json


def analyze_csv_data(csv_content_list):
    """
    Analyze CSV data and return summary statistics

    Args:
        csv_content_list: List of dictionaries with 'filename' and 'content' keys

    Returns:
        dict: Analysis results
    """
    results = {
        "total_files": len(csv_content_list),
        "files_analyzed": [],
        "summary": {},
        "errors": []
    }

    for file_data in csv_content_list:
        filename = file_data.get("filename", "unknown")
        content = file_data.get("content", "")

        try:
            # Parse CSV content
            df = pd.read_csv(StringIO(content))

            # Get numeric columns only
            numeric_columns = df.select_dtypes(
                include=['number']).columns.tolist()

            file_analysis = {
                "filename": filename,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "numeric_columns": numeric_columns,
                "column_sums": {},
                "column_means": {},
                "missing_values": {}
            }

            # Calculate sums and means for numeric columns
            for col in numeric_columns:
                file_analysis["column_sums"][col] = float(df[col].sum())
                file_analysis["column_means"][col] = float(df[col].mean())
                file_analysis["missing_values"][col] = int(
                    df[col].isnull().sum())

            # Add non-numeric column info
            non_numeric_cols = [
                col for col in df.columns if col not in numeric_columns]
            file_analysis["text_columns"] = non_numeric_cols

            for col in non_numeric_cols:
                file_analysis["missing_values"][col] = int(
                    df[col].isnull().sum())

            results["files_analyzed"].append(file_analysis)

        except Exception as e:
            error_msg = f"Error analyzing {filename}: {str(e)}"
            results["errors"].append(error_msg)

    # Global summary across all files
    if results["files_analyzed"]:
        results["summary"] = {
            "total_rows_all_files": sum(f["total_rows"] for f in results["files_analyzed"]),
            "average_columns_per_file": sum(f["total_columns"] for f in results["files_analyzed"]) / len(results["files_analyzed"]),
            "most_common_numeric_columns": _get_most_common_columns(results["files_analyzed"])
        }

    return results


def _get_most_common_columns(files_analyzed):
    """Helper function to find most common numeric columns across files"""
    column_frequency = {}
    for file_data in files_analyzed:
        for col in file_data["numeric_columns"]:
            column_frequency[col] = column_frequency.get(col, 0) + 1

    # Sort by frequency
    return sorted(column_frequency.items(), key=lambda x: x[1], reverse=True)


def format_analysis_results(analysis_results):
    """
    Format analysis results for display

    Args:
        analysis_results: Dictionary from analyze_csv_data()

    Returns:
        str: Formatted text for display
    """
    if not analysis_results["files_analyzed"]:
        return "No data to analyze or all files had errors."

    output = []
    output.append("🔬 DATA ANALYSIS RESULTS")
    output.append("=" * 50)
    output.append(
        f"📊 Total files processed: {analysis_results['total_files']}")
    output.append(
        f"✅ Successfully analyzed: {len(analysis_results['files_analyzed'])}")

    if analysis_results["errors"]:
        output.append(f"❌ Errors: {len(analysis_results['errors'])}")
        for error in analysis_results["errors"]:
            output.append(f"   • {error}")

    output.append("\n📈 SUMMARY STATISTICS")
    output.append("-" * 30)
    summary = analysis_results["summary"]
    output.append(
        f"Total rows across all files: {summary['total_rows_all_files']}")
    output.append(
        f"Average columns per file: {summary['average_columns_per_file']:.1f}")

    if summary["most_common_numeric_columns"]:
        output.append("\nMost common numeric columns:")
        for col, freq in summary["most_common_numeric_columns"][:5]:
            output.append(f"   • {col}: appears in {freq} file(s)")

    output.append("\n📋 DETAILED FILE ANALYSIS")
    output.append("-" * 30)

    for file_data in analysis_results["files_analyzed"]:
        output.append(f"\n📄 File: {file_data['filename']}")
        output.append(
            f"   Rows: {file_data['total_rows']}, Columns: {file_data['total_columns']}")

        if file_data["column_sums"]:
            output.append("   Column sums:")
            for col, sum_val in file_data["column_sums"].items():
                output.append(f"      {col}: {sum_val:,.2f}")

        if file_data["text_columns"]:
            output.append(
                f"   Text columns: {', '.join(file_data['text_columns'])}")

    return "\n".join(output)
