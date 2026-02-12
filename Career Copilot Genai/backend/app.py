from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import boto3
import json
import uuid
from datetime import datetime
import requests
import pdfplumber
from docx import Document
import io


# LocalStack endpoint
LOCALSTACK_ENDPOINT = "http://localhost:4566"

# Ollama endpoint (runs locally)
OLLAMA_URL = "http://localhost:11434/api/generate"

# AWS Resources (LocalStack)
s3 = boto3.client(
    "s3",
    endpoint_url=LOCALSTACK_ENDPOINT,
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=LOCALSTACK_ENDPOINT,
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

BUCKET_NAME = "career-copilot-bucket"
TABLE_NAME = "CareerCopilotResults"
table = dynamodb.Table(TABLE_NAME)

app = FastAPI()


# Request schema (input validation)
class MatchRequest(BaseModel):
    resume_text: str
    job_description: str
@app.get("/")
def home():
    return {"message": "Career Copilot API is running"}


# Function to call Ollama Llama3
def call_llama3(resume_text, job_description):

    prompt = f"""
You are an ATS resume evaluator.

Return ONLY a valid JSON object.
Do not include any explanation.
Do not include markdown.
Do not wrap with ```json.

The JSON must contain exactly these keys:
match_score (integer 0-100),
missing_keywords (list of strings),
strengths (list of strings),
improvements (list of strings),
recommended_resume_bullets (list of strings),
cover_letter_intro (string)

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    payload = {
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        result = response.json()

        output_text = result.get("response", "")
        print("RAW MODEL OUTPUT:", output_text)

        return json.loads(output_text)

    except Exception as e:
        return {
            "match_score": 0,
            "missing_keywords": [],
            "strengths": [],
            "improvements": [f"Error calling Llama3 or parsing JSON: {str(e)}"],
            "recommended_resume_bullets": [],
            "cover_letter_intro": ""
        }


# API endpoint
@app.post("/match")
def match_resume(request: MatchRequest):
    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    # Call GenAI model
    analysis = call_llama3(request.resume_text, request.job_description)

    # Store output JSON in S3
    s3_key = f"results/{request_id}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(analysis, indent=2),
        ContentType="application/json"
    )

    # Store metadata in DynamoDB
    table.put_item(
        Item={
            "request_id": request_id,
            "timestamp": timestamp,
            "s3_key": s3_key,
            "bucket": BUCKET_NAME,
            "match_score": str(analysis.get("match_score", 0))
        }
    )

    return {
        "message": "Resume analysis completed successfully",
        "request_id": request_id,
        "match_score": analysis.get("match_score", 0),
        "s3_result_file": s3_key
    }
def extract_text_from_resume(filename: str, file_bytes: bytes) -> str:
    filename = filename.lower()

    # TXT
    if filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")

    # PDF
    elif filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    # DOCX
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()

    else:
        return ""
@app.post("/match-upload")
async def match_resume_upload(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    # Read file bytes
    file_bytes = await resume_file.read()

    # Extract resume text
    resume_text = extract_text_from_resume(resume_file.filename, file_bytes)

    if not resume_text.strip():
        return {"error": "Could not extract text. Please upload PDF, DOCX, or TXT resume."}

    # Call AI model
    analysis = call_llama3(resume_text, job_description)

    # Store output JSON in S3
    s3_key = f"results/{request_id}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(analysis, indent=2),
        ContentType="application/json"
    )

    # Store metadata in DynamoDB
    table.put_item(
        Item={
            "request_id": request_id,
            "timestamp": timestamp,
            "s3_key": s3_key,
            "bucket": BUCKET_NAME,
            "match_score": str(analysis.get("match_score", 0))
        }
    )

    return {
        "message": "Resume upload analysis completed successfully",
        "request_id": request_id,
        "match_score": analysis.get("match_score", 0),
        "s3_result_file": s3_key
    }

