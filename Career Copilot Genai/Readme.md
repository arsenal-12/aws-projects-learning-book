# 🤖 Career Copilot (GenAI Resume Matcher) - LocalStack + Ollama + FastAPI

![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![LocalStack](https://img.shields.io/badge/LocalStack-AWS%20Simulation-purple)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-blue)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange)
![AWS S3](https://img.shields.io/badge/AWS-S3-green)
![DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-yellow)
![Python](https://img.shields.io/badge/Python-3.12+-brightgreen)

This project demonstrates a **Generative AI powered Resume Matching System** by integrating a **local LLM (Ollama)** with a backend API built using **FastAPI**, and storing results using AWS services simulated locally via **LocalStack running inside Docker**.

When a user submits **resume text + job description**, the FastAPI backend sends a structured prompt to the LLM, generates an ATS-style evaluation, and stores the final JSON output in **S3** while saving metadata in **DynamoDB**.

💡 This project was built to gain hands-on experience with **GenAI + Cloud workflows** without requiring a paid AWS account.

---

## 🚀 Key Features

✅ Resume vs Job Description matching (ATS-style evaluation)  
✅ Generates match score (0–100)  
✅ Extracts missing keywords  
✅ Highlights strengths & improvement areas  
✅ Suggests better resume bullet points  
✅ Generates cover letter introduction  
✅ Stores AI output JSON in **S3**  
✅ Stores metadata in **DynamoDB**  
✅ Fully testable using Swagger UI (`/docs`)  

---

## 🏗️ Architecture (GenAI + Cloud Workflow)

### 🔄 Workflow Steps

1. User submits Resume + Job Description through Swagger UI / Postman
2. FastAPI backend sends prompt to Ollama (local LLM)
3. Ollama generates structured JSON analysis output
4. FastAPI stores output JSON in LocalStack S3 bucket (`results/`)
5. FastAPI stores metadata in LocalStack DynamoDB table

---

### 📌 Architecture Flow Diagram

```text
User (Swagger UI / Browser / Postman)
        |
        v
FastAPI Backend (Uvicorn)
        |
        v
Ollama (Local LLM Model)
(Llama3 / Phi3 Mini)
        |
        v
AI Resume Analysis Output (JSON)
        |
        +------------------------------+
        |                              |
        v                              v
LocalStack S3 Bucket                LocalStack DynamoDB Table
career-copilot-bucket               CareerCopilotResults
(results/<request_id>.json)         (request_id, score, timestamp)

📷 Architecture image available in:
architecture/architecture.png

🛠️ Technologies Used

Docker

LocalStack (AWS service simulation)

AWS CLI

Python 3.12+

FastAPI

Uvicorn

Ollama (Local LLM inference)

Amazon S3 (Simulated)

Amazon DynamoDB (Simulated)

📂 Project Structure
02-career-copilot-genai/
│
├── backend/
│   ├── app.py
│   └── requirements.txt
│
├── architecture/
│   └── architecture.png
│
├── sample-output/
│   └── sample-result.json
│
├── screenshots/
│   ├── swagger-ui.png
│   ├── swagger-response.png
│   ├── s3-results.png
│   ├── dynamodb-scan.png
│   └── ollama-model.png
│
└── README.md

⚙️ Prerequisites

Install the following tools before running the project:

Docker Desktop

Python 3.12+

AWS CLI

Ollama (Local LLM)

🚀 Setup and Execution
1️⃣ Start LocalStack using Docker

Run LocalStack container:

docker run --rm -it -p 4566:4566 localstack/localstack


LocalStack will run at:

http://localhost:4566

2️⃣ Configure AWS CLI Credentials (Windows PowerShell)

LocalStack accepts dummy credentials:

$env:AWS_ACCESS_KEY_ID="test"
$env:AWS_SECRET_ACCESS_KEY="test"
$env:AWS_DEFAULT_REGION="us-east-1"


Test connection:

aws --endpoint-url=http://localhost:4566 s3 ls

3️⃣ Create an S3 Bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://career-copilot-bucket

4️⃣ Create a DynamoDB Table
aws --endpoint-url=http://localhost:4566 dynamodb create-table `
  --table-name CareerCopilotResults `
  --attribute-definitions AttributeName=request_id,AttributeType=S `
  --key-schema AttributeName=request_id,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST


Verify table creation:

aws --endpoint-url=http://localhost:4566 dynamodb list-tables

🤖 Ollama Setup (Local GenAI Model)
5️⃣ Install Ollama

Download Ollama from:

https://ollama.com/

6️⃣ Download a Model

Install Llama3:

ollama pull llama3


If your laptop RAM is low, use a smaller model:

ollama pull phi3:mini


Verify installed models:

ollama list

🧠 FastAPI Backend Setup
7️⃣ Install Python Dependencies

Go inside backend folder:

cd backend


Install required packages:

pip install -r requirements.txt

8️⃣ Run the FastAPI Server

Start backend using Uvicorn:

uvicorn app:app --reload


Your backend will run at:

http://127.0.0.1:8000

🧪 Testing the API (Swagger UI)

Open Swagger UI:

http://127.0.0.1:8000/docs


Use endpoint:

✅ POST /match

Example input:

{
  "resume_text": "I have experience in Python, AWS, FastAPI, and DynamoDB.",
  "job_description": "Looking for Backend Developer with Python, AWS, DynamoDB and API development experience."
}


Example response:

{
  "message": "Resume analysis completed successfully",
  "request_id": "a44fb4a2-3d39-425c-9780-76f837652fcb",
  "match_score": 85,
  "s3_result_file": "results/a44fb4a2-3d39-425c-9780-76f837652fcb.json"
}

📤 Output Storage
🪣 S3 Output Location

AI output JSON will be stored in:

career-copilot-bucket/results/<request_id>.json


To list stored results:

aws --endpoint-url=http://localhost:4566 s3 ls s3://career-copilot-bucket/results/

🗄️ DynamoDB Storage

Metadata stored in DynamoDB includes:

request_id

timestamp

match_score

s3_key

bucket

To view stored items:

aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name CareerCopilotResults

📄 Sample Output

A sample output file is available inside:

sample-output/sample-result.json


Example output:

{
  "match_score": 85,
  "missing_keywords": ["Docker", "CI/CD", "REST API"],
  "strengths": ["Python experience", "AWS knowledge"],
  "improvements": ["Add more backend project examples"],
  "recommended_resume_bullets": [
    "Built a FastAPI-based GenAI Resume Matching backend using Ollama and LocalStack."
  ],
  "cover_letter_intro": "I am excited to apply for this role because..."
}

📸 Screenshots

Proof of execution screenshots:

📌 Swagger UI Request/Response

📌 Swagger Response Output

📌 S3 Stored Results Proof

📌 DynamoDB Scan Output Proof

📌 Ollama Model Installed Proof

📌 Notes

⚠️ This project uses LocalStack Community Edition, so AWS services are simulated locally.

✅ This workflow can be deployed on real AWS by replacing LocalStack endpoints with actual AWS services.

Example real-world production version could include:

API Gateway + Lambda

Amazon Bedrock (Claude / Nova)

CloudWatch Monitoring

Cognito Authentication

S3 + DynamoDB production deployment

👩‍💻 Author

Indhu Shree Prakash
📍 Master's Student | Cloud & Data Engineering Enthusiast
🚀 Exploring AWS, GenAI, Serverless & DevOps Workflows
