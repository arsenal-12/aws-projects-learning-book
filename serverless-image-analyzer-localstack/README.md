# 🖼️ Serverless Image Analyzer (LocalStack + Docker)

This project demonstrates an **event-driven serverless architecture** by simulating AWS services locally using **LocalStack** running inside **Docker**.

When a file (image) is uploaded to an S3 bucket inside the `uploads/` folder, an S3 event automatically triggers a Lambda function. The Lambda function performs mock image analysis (simulated AI label detection), stores the output as a JSON file in the `results/` folder of the same bucket, and saves metadata into a DynamoDB table.

This project was built to gain hands-on experience with AWS serverless workflows without requiring a paid AWS account.

---

## 🚀 Key Features

- Local AWS simulation using **LocalStack Community Edition**
- Docker-based environment (**portable & reproducible**)
- Uploading a file triggers processing automatically (**event-driven system**)
- Lambda generates mock labels and metadata
- Output stored in:
  - S3 `results/` folder (JSON file)
  - DynamoDB table (record of upload + processing)

---

## 🏗️ Architecture (Event-Driven Workflow)

### **Workflow**
1. User uploads an image to S3 `uploads/`
2. S3 event triggers Lambda function automatically
3. Lambda processes the uploaded file and generates mock labels
4. Lambda saves output JSON into S3 `results/`
5. Lambda inserts metadata into DynamoDB

### **Architecture Flow**

User Upload (AWS CLI)
|
v
LocalStack S3 Bucket (uploads/)
|
v
S3 ObjectCreated Event Trigger
|
v
LocalStack Lambda Function
|
+----------------------------+
| |
v v
S3 results/ folder (JSON Output) DynamoDB Table (Metadata Storage)


---

## 🛠️ Technologies Used

- Docker
- LocalStack (AWS service simulation)
- AWS CLI
- Python 3.12
- Amazon S3 (Simulated)
- AWS Lambda (Simulated)
- Amazon DynamoDB (Simulated)

---

## 📂 Project Structure
01-serverless-image-analyzer-localstack/
│
├── lambda_code/
│ └── lambda_function.py
│
├── architecture/
│ └── architecture.png
│
├── sample-output/
│ └── testdynamo.jpg.json
│
├── screenshots/
│ ├── s3-uploads.png
│ ├── s3-results.png
│ └── dynamodb-scan.png
│
└── README.md

---

## ⚙️ Prerequisites

Install the following tools before running the project:

- Docker Desktop  
- Python 3.12+
- AWS CLI

---

## 🚀 Setup and Execution

### 1️⃣ Start LocalStack using Docker

Run LocalStack container:

```bash
docker run --rm -it -p 4566:4566 -p 4510-4559:4510-4559 -e SERVICES=s3,lambda,dynamodb -v /var/run/docker.sock:/var/run/docker.sock localstack/localstack

LocalStack will run at:

http://localhost:4566

2️⃣ Configure AWS CLI Credentials (PowerShell)

LocalStack accepts dummy credentials.

$env:AWS_ACCESS_KEY_ID="test"
$env:AWS_SECRET_ACCESS_KEY="test"
$env:AWS_DEFAULT_REGION="us-east-1"


Test connection:

aws --endpoint-url=http://localhost:4566 s3 ls

3️⃣ Create an S3 Bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://image-analyzer-bucket

4️⃣ Create a DynamoDB Table
aws --endpoint-url=http://localhost:4566 dynamodb create-table `
  --table-name ImageAnalysisResults `
  --attribute-definitions AttributeName=image_id,AttributeType=S `
  --key-schema AttributeName=image_id,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST


Verify:

aws --endpoint-url=http://localhost:4566 dynamodb list-tables

🧠 Lambda Deployment
5️⃣ Create Lambda ZIP Package (Windows PowerShell)

Go to the lambda folder:

cd lambda_code


Zip the Lambda file:

Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force

6️⃣ Create Lambda Function
aws --endpoint-url=http://localhost:4566 lambda create-function `
  --function-name image-analyzer-lambda `
  --runtime python3.12 `
  --handler lambda_function.lambda_handler `
  --role arn:aws:iam::000000000000:role/lambda-role `
  --zip-file fileb://function.zip

7️⃣ Allow S3 to Invoke Lambda
aws --endpoint-url=http://localhost:4566 lambda add-permission `
  --function-name image-analyzer-lambda `
  --statement-id s3invoke1 `
  --action lambda:InvokeFunction `
  --principal s3.amazonaws.com `
  --source-arn arn:aws:s3:::image-analyzer-bucket

🔔 Enable S3 Event Trigger
8️⃣ Create Notification Configuration File

Create notification.json inside your project folder:

{
  "LambdaFunctionConfigurations": [
    {
      "Id": "UploadTrigger",
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:image-analyzer-lambda",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            { "Name": "prefix", "Value": "uploads/" }
          ]
        }
      }
    }
  ]
}

9️⃣ Attach Notification Trigger to S3 Bucket
aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration `
  --bucket image-analyzer-bucket `
  --notification-configuration file://notification.json


Verify trigger:

aws --endpoint-url=http://localhost:4566 s3api get-bucket-notification-configuration --bucket image-analyzer-bucket

📤 Upload Image to Trigger Lambda
🔟 Upload an Image to uploads/

Create a test image file:

echo "test image" > testdynamo.jpg


Upload to S3:

aws --endpoint-url=http://localhost:4566 s3 cp testdynamo.jpg s3://image-analyzer-bucket/uploads/testdynamo.jpg


This automatically triggers the Lambda function.

✅ Verification
✅ Check uploaded file in uploads/
aws --endpoint-url=http://localhost:4566 s3 ls s3://image-analyzer-bucket/uploads/

✅ Check generated JSON output in results/
aws --endpoint-url=http://localhost:4566 s3 ls s3://image-analyzer-bucket/results/

✅ Check DynamoDB table records
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name ImageAnalysisResults

📄 Sample Output

Example JSON output stored in:

results/testdynamo.jpg.json


Example content:

{
  "bucket": "image-analyzer-bucket",
  "image_id": "uploads/testdynamo.jpg",
  "uploaded_file": "uploads/testdynamo.jpg",
  "timestamp": "2026-02-07T19:55:12.169378",
  "labels": [
    { "Name": "Person", "Confidence": 98.5 },
    { "Name": "Car", "Confidence": 85.2 },
    { "Name": "Laptop", "Confidence": 90.1 }
  ]
}

📸 Screenshots
S3 Upload Folder Proof

S3 Results Folder Proof

DynamoDB Scan Output Proof

📌 Notes

This project uses mock AI label detection because Amazon Rekognition is not fully supported in LocalStack Community Edition.

The same workflow can be deployed to real AWS by replacing mock logic with actual Rekognition API calls.

👩‍💻 Author

Indhu Shree Prakash


---

