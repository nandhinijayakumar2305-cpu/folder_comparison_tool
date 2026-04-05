import os
import pandas as pd
from datetime import datetime


def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_excel_report(comparison_result, excel_diffs, output_dir):
    """Export comparison results to Excel report"""
    timestamp = get_timestamp()
    filename = os.path.join(output_dir, f"comparison_report_{timestamp}.xlsx")

    try:
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:

            # Sheet 1: Summary
            summary_data = {
                "Category": ["Total Files (Folder 1)", "Total Files (Folder 2)",
                              "New Files", "Deleted Files",
                              "Modified Files", "Unchanged Files", "Renamed Files"],
                "Count": [
                    comparison_result.get("total_folder1", 0),
                    comparison_result.get("total_folder2", 0),
                    len(comparison_result.get("new", [])),
                    len(comparison_result.get("deleted", [])),
                    len(comparison_result.get("modified", [])),
                    len(comparison_result.get("unchanged", [])),
                    len(comparison_result.get("renamed", []))
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

            # Sheet 2: New Files
            if comparison_result.get("new"):
                pd.DataFrame({"New Files": comparison_result["new"]}).to_excel(
                    writer, sheet_name="New Files", index=False)

            # Sheet 3: Deleted Files
            if comparison_result.get("deleted"):
                pd.DataFrame({"Deleted Files": comparison_result["deleted"]}).to_excel(
                    writer, sheet_name="Deleted Files", index=False)

            # Sheet 4: Modified Files
            if comparison_result.get("modified"):
                pd.DataFrame({"Modified Files": comparison_result["modified"]}).to_excel(
                    writer, sheet_name="Modified Files", index=False)

            # Sheet 5: Renamed Files
            if comparison_result.get("renamed"):
                renamed_data = [{
                    "Original File": r["original"],
                    "Renamed To": r["renamed_to"]
                } for r in comparison_result["renamed"]]
                pd.DataFrame(renamed_data).to_excel(
                    writer, sheet_name="Renamed Files", index=False)

            # Sheet 6: Excel Differences
            if excel_diffs:
                all_diffs = []
                for item in excel_diffs:
                    for d in item["diff"].get("differences", []):
                        all_diffs.append({
                            "File": item["file"],
                            "Type": d["type"],
                            "Detail": d["detail"]
                        })
                if all_diffs:
                    pd.DataFrame(all_diffs).to_excel(
                        writer, sheet_name="Excel Differences", index=False)

        return filename

    except Exception as e:
        return f"Error generating Excel report: {str(e)}"


def export_html_report(comparison_result, excel_diffs, ai_summary, output_dir):
    """Export comparison results to HTML report"""
    timestamp = get_timestamp()
    filename = os.path.join(output_dir, f"comparison_report_{timestamp}.html")

    def make_list(items):
        if not items:
            return "<p>None</p>"
        return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

    def make_excel_section():
        if not excel_diffs:
            return "<p>No Excel files were modified.</p>"
        html = ""
        for item in excel_diffs:
            html += f"<h4>📄 {item['file']}</h4><ul>"
            diffs = item["diff"].get("differences", [])
            if not diffs:
                html += "<li>No differences found</li>"
            for d in diffs:
                html += f"<li><b>{d['type']}:</b> {d['detail']}</li>"
            html += "</ul>"
        return html

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Folder Comparison Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        h4 {{ color: #2980b9; }}
        .card {{ background: white; padding: 20px; margin: 20px 0;
                 border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
        .stat {{ background: #3498db; color: white; padding: 15px;
                border-radius: 8px; text-align: center; }}
        .stat h3 {{ margin: 0; font-size: 28px; }}
        .stat p {{ margin: 5px 0 0; font-size: 13px; }}
        .new {{ background: #27ae60; }}
        .deleted {{ background: #e74c3c; }}
        .modified {{ background: #f39c12; }}
        .renamed {{ background: #9b59b6; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 5px 0; }}
        .ai-box {{ background: #eaf4fb; border-left: 5px solid #3498db;
                   padding: 15px; border-radius: 5px; white-space: pre-wrap; }}
        .timestamp {{ color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>📁 Folder Comparison Report</h1>
    <p class="timestamp">Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <div class="card">
        <h2>📊 Summary</h2>
        <div class="summary-grid">
            <div class="stat new">
                <h3>{len(comparison_result.get('new', []))}</h3>
                <p>New Files</p>
            </div>
            <div class="stat deleted">
                <h3>{len(comparison_result.get('deleted', []))}</h3>
                <p>Deleted Files</p>
            </div>
            <div class="stat modified">
                <h3>{len(comparison_result.get('modified', []))}</h3>
                <p>Modified Files</p>
            </div>
            <div class="stat renamed">
                <h3>{len(comparison_result.get('renamed', []))}</h3>
                <p>Renamed Files</p>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>🤖 AI Impact Summary</h2>
        <div class="ai-box">{ai_summary}</div>
    </div>

    <div class="card">
        <h2>🆕 New Files</h2>
        {make_list(comparison_result.get('new', []))}
    </div>

    <div class="card">
        <h2>🗑️ Deleted Files</h2>
        {make_list(comparison_result.get('deleted', []))}
    </div>

    <div class="card">
        <h2>✏️ Modified Files</h2>
        {make_list(comparison_result.get('modified', []))}
    </div>

    <div class="card">
        <h2>🔄 Renamed Files</h2>
        {make_list([f"{r['original']} → {r['renamed_to']}" for r in comparison_result.get('renamed', [])])}
    </div>

    <div class="card">
        <h2>📋 Excel Differences</h2>
        {make_excel_section()}
    </div>

</body>
</html>
"""

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        return filename
    except Exception as e:
        return f"Error generating HTML report: {str(e)}"