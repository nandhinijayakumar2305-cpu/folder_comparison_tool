import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(comparison_result, excel_diffs):
    """Build a prompt for AI summary"""

    new_files = comparison_result.get("new", [])
    deleted_files = comparison_result.get("deleted", [])
    modified_files = comparison_result.get("modified", [])
    renamed_files = comparison_result.get("renamed", [])

    prompt = f"""
You are a release validation expert. Analyze the following folder comparison results and generate a clear, business-friendly impact summary.

=== FOLDER COMPARISON RESULTS ===
- Total files in Folder 1: {comparison_result.get('total_folder1', 0)}
- Total files in Folder 2: {comparison_result.get('total_folder2', 0)}
- New files added: {len(new_files)}
- Files deleted: {len(deleted_files)}
- Files modified: {len(modified_files)}
- Files renamed: {len(renamed_files)}

New Files: {', '.join(new_files[:10]) if new_files else 'None'}
Deleted Files: {', '.join(deleted_files[:10]) if deleted_files else 'None'}
Modified Files: {', '.join(modified_files[:10]) if modified_files else 'None'}
Renamed Files: {', '.join([f"{r['original']} → {r['renamed_to']}" for r in renamed_files[:5]]) if renamed_files else 'None'}
"""

    if excel_diffs:
        prompt += "\n=== EXCEL CHANGES ===\n"
        for item in excel_diffs[:5]:
            prompt += f"\nFile: {item['file']}\n"
            diffs = item["diff"].get("differences", [])
            for d in diffs[:10]:
                prompt += f"  - {d['type']}: {d['detail']}\n"

    prompt += """
=== YOUR TASK ===
Generate a short executive summary (5-8 lines) covering:
1. Overall impact (low / medium / high risk)
2. Key changes detected
3. Any critical files modified
4. Recommendation for release team

Keep it simple, clear, and professional.
"""

    return prompt


def generate_ai_summary(comparison_result, excel_diffs):
    """Call Groq API and return AI-generated summary"""
    try:
        prompt = build_prompt(comparison_result, excel_diffs)

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional release validation expert who writes clear impact summaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.5
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ AI Summary could not be generated: {str(e)}"