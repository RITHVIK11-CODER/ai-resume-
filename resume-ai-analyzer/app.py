import os
import sys
from flask import Flask, jsonify, request, render_template

# Ensure the project directory is on sys.path so utils can always be imported
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.resume_parser import extract_resume_text
from utils.resume_matcher import analyze_resume

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

MAX_FILE_SIZE = 4 * 1024 * 1024  # 4 MB
MAX_JOB_DESCRIPTION = 20000


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api", methods=["GET", "POST"])
def analyze():
    if request.method == "GET":
        return jsonify({
            "name": "ResumeAI API",
            "status": "ok",
            "message": "Submit a POST request with a PDF resume and job description to analyze."
        })

    if "resume" not in request.files:
        return jsonify({"error": "Please upload a PDF resume."}), 400

    resume = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()

    if not resume or not resume.filename:
        return jsonify({"error": "Please choose a resume file to upload."}), 400

    if not resume.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    if not job_description:
        return jsonify({"error": "Please enter a job description."}), 400

    if len(job_description) > MAX_JOB_DESCRIPTION:
        return jsonify({"error": "Job description is too long (maximum 20,000 characters)."}), 400

    try:
        # Read the uploaded PDF file directly into memory (not saved to disk)
        file_bytes = resume.read(MAX_FILE_SIZE + 1)

        if not file_bytes:
            return jsonify({"error": "The uploaded PDF file is empty."}), 400

        if len(file_bytes) > MAX_FILE_SIZE:
            return jsonify({"error": "PDF file must be 4 MB or smaller."}), 413

        if not file_bytes.startswith(b"%PDF-"):
            return jsonify({"error": "Please upload a valid PDF file."}), 400

        resume_text = extract_resume_text(file_bytes)
        result = analyze_resume(resume_text, job_description)

        return jsonify(result)

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    except Exception:
        app.logger.exception("Analysis failed")
        return jsonify({"error": "Analysis failed. Please try again with another file."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
