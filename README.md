# Resume Analyzer

A Flask-based application that allows users to upload a PDF resume and have it analyzed by OpenAI's GPT API. The application provides a summary of the individual, generates a new objective, performs spell and grammar checks, and lists recommendations for improving the resume.

## Usage

### Prerequisites

- Python 3.9
- virtualenv
- Docker (optional)

### Installation

1. Clone the repository:

```
git clone https://github.com/yourusername/resume-analyzer.git
cd resume-analyzer
```

2. Create and activate a virtual environment:

```
virtualenv venv
source venv/bin/activate # On Windows, use venv\Scripts\activate
```

3. Install the required packages:

```
pip install -r requirements.txt
```

4. Create a `.env` file in the project directory with the following content:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_ENGINE=gpt-3.5-turbo
OPENAI_MAX_TOKENS=2048
OPENAI_TEMPERATURE=0.5
```

Replace `your_openai_api_key` with your actual OpenAI API key.

5. Run the application:

```
flask run
```

6. Open your browser and go to `http://localhost:5000` to use the web interface.

## Docker Instructions

1. Build the Docker image:

```
docker build -t resume-analyzer .
```

2. Run the Docker container:

```
docker run -p 5000:5000 --env-file .env resume-analyzer
```

The application should now be accessible at `http://localhost:5000`.

## API Endpoints

- `POST /api/analyze` - Analyzes a resume file and returns a JSON object with the results.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
