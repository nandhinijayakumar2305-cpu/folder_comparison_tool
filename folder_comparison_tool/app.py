from flask import Flask, render_template, request, send_file
import os
from dotenv import load_dotenv
from comparator import compare_folders
from excel_compare import compare_excel_files
from ai_summary import generate_ai_summary
from report_generator import export_excel_report, export_html_report

load_dotenv()

app = Flask(__name__)

REPORTS_DIR = "reports"
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():
    folder1 = request.form.get("folder1", "").strip()
    folder2 = request.form.get("folder2", "").strip()

    if not os.path.isdir(folder1) or not os.path.isdir(folder2):
        return render_template("index.html", 
               error="❌ Invalid folder paths. Please check and try again.")

    comparison_result = compare_folders(folder1, folder2)

    excel_diffs = []
    for file in comparison_result["modified"]:
        if file.endswith((".xlsx", ".xlsm")):
            diff = compare_excel_files(
                os.path.join(folder1, file),
                os.path.join(folder2, file)
            )
            excel_diffs.append({"file": file, "diff": diff})

    ai_summary = generate_ai_summary(comparison_result, excel_diffs)

    excel_report_path = export_excel_report(
                            comparison_result, excel_diffs, REPORTS_DIR)
    html_report_path = export_html_report(
                            comparison_result, excel_diffs, ai_summary, REPORTS_DIR)

    return render_template(
        "results.html",
        folder1=folder1,
        folder2=folder2,
        result=comparison_result,
        excel_diffs=excel_diffs,
        ai_summary=ai_summary,
        excel_report=excel_report_path,
        html_report=html_report_path
    )


@app.route("/download/<path:filename>")
def download(filename):
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)