import os
import openai
import requests
from flask import Flask, request, jsonify, render_template, Response, session
from flask_restful import Resource, Api
from flask_session import Session
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from io import BytesIO

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set OpenAI parameters with defaults
openai_engine = os.getenv("OPENAI_ENGINE", "gpt-3.5-turbo")
openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 150))
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.5))

# Initialize Flask application
app = Flask(__name__)

# Configure session
app.config['SECRET_KEY'] = os.getenv("SESSION_SECRET_KEY", "supersecretkey")
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

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
    prompt = f"Analyze the following resume: {resume_text}"
    response = requests.post(
        f"https://api.openai.com/v1/engines/{openai_engine}/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        },
        json={
            "prompt": prompt,
            "max_tokens": openai_max_tokens,
            "n": 1,
            "stop": None,
            "temperature": openai_temperature,
        },
        stream=True,
    )

    return response


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route('/submit', methods=['POST'])
def submit():
    if 'resume' not in request.files:
        return jsonify(error='No resume file provided'), 400

    resume_file = request.files['resume']
    if not allowed_file(resume_file.filename):
        return jsonify(error='Invalid file type'), 400

    resume_text = read_pdf(resume_file.stream)
    session['resume_text'] = resume_text

    return jsonify(status='ok')


@app.route('/analyze', methods=['GET'])
def analyze():
    resume_text = session.get('resume_text', None)
    if not resume_text:
        return jsonify(error='No resume text found'), 400

    response = analyze_resume(resume_text)

    def generate():
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return Response(generate(), content_type="text/event-stream")


if __name__ == "__main__":
    app.run(debug=enable_debug, host="0.0.0.0")
