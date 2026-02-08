import json
import boto3
from datetime import datetime
from decimal import Decimal

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("ImageAnalysisResults")


def convert_floats_to_decimal(obj):
    """
    DynamoDB does NOT allow float type.
    So we convert float -> Decimal.
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    else:
        return obj


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    if "Records" not in event:
        return {"statusCode": 200, "body": "No S3 Records found"}

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    # process only uploads/
    if not key.startswith("uploads/"):
        return {"statusCode": 200, "body": "Skipped (not uploads/)"}

    timestamp = datetime.utcnow().isoformat()

    # Fake labels output
    labels = [
        {"Name": "Person", "Confidence": 98.5},
        {"Name": "Car", "Confidence": 85.2},
        {"Name": "Laptop", "Confidence": 90.1}
    ]

    result = {
        "image_id": key,   # partition key
        "bucket": bucket,
        "uploaded_file": key,
        "timestamp": timestamp,
        "labels": labels
    }

    # save JSON to results folder
    result_key = key.replace("uploads/", "results/") + ".json"

    s3.put_object(
        Bucket=bucket,
        Key=result_key,
        Body=json.dumps(result),
        ContentType="application/json"
    )

    # Convert float to Decimal for DynamoDB
    dynamo_item = convert_floats_to_decimal(result)

    # save to DynamoDB
    table.put_item(Item=dynamo_item)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Stored in S3 + DynamoDB",
            "result_file": result_key
        })
    }
