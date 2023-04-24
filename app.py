import os
import openai
from flask import Flask, request, jsonify, render_template
from flask_restful import Resource, Api
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from io import BytesIO
from textblob import TextBlob

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set OpenAI parameters with defaults
openai_engine = os.getenv("OPENAI_ENGINE", "gpt-3.5-turbo")
openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 150))
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.5))

# Initialize Flask application
app = Flask(__name__)
api = Api(app)

enable_debug = os.getenv("ENABLE_DEBUG", "false").lower() == "true"

# Configure uploads
pdfs = UploadSet("pdfs", DOCUMENTS)
app.config["UPLOADED_PDFS_DEST"] = "uploads"
configure_uploads(app, pdfs)

# Define helper functions


def read_pdf(pdf_stream):
    pdf_reader = PdfReader(pdf_stream)
    text = ""
    for page in pdf_reader.pages:
        text += "".join(page.extract_text())
    return text


def analyze_resume(resume_text):
    # Analyze the resume using OpenAI GPT API
    prompt = f"Analyze the following resume in 400 characters or less, and based solely on the data in the resume, make a conculsion if this is a potential candidate for a Site Reliability Engineer: {resume_text}"
    response = openai.ChatCompletion.create(
        model=openai_engine,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=openai_max_tokens,
        n=1,
        stop=None,
        temperature=openai_temperature,
    )
    return response.choices[0].message['content'].strip()


class ResumeApi(Resource):
    def post(self):
        if "pdf" not in request.files:
            return {"error": "No file provided."}, 400

        pdf = request.files["pdf"]

        if pdf.filename == "":
            return {"error": "No file provided."}, 400

        if not pdfs.file_allowed(pdf, pdf.filename):
            return {"error": "Invalid file format."}, 400

        pdf_stream = BytesIO(pdf.read())
        resume_text = read_pdf(pdf_stream)
        analysis = analyze_resume(resume_text)
        return {"analysis": analysis}


api.add_resource(ResumeApi, "/api/analyze")


@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None
    if request.method == "POST":
        analysis = ResumeApi().post()
    return render_template("index.html", analysis=analysis)


if __name__ == "__main__":
    app.run(debug=enable_debug, host="0.0.0.0")
