import boto3
import os
import json

# Initialize SNS Client
sns_client = boto3.client(
    "sns",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

def send_sns_notification(email, appointment_details):
    """
    Publishes a message to the SNS topic.
    """
    topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")
    message = f"Your appointment details: {appointment_details}"
    
    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject="Appointment Confirmation",
    )

    return response

# Initialize Lambda Client
lambda_client = boto3.client(
    "lambda",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

def trigger_lambda(email, date, time):
    """
    Invokes AWS Lambda function for appointment notifications.
    """
    lambda_function_arn = os.getenv("AWS_LAMBDA_FUNCTION_ARN")
    payload = json.dumps({"email": email, "date": date, "time": time})

    response = lambda_client.invoke(
        FunctionName=lambda_function_arn,
        InvocationType="RequestResponse",
        Payload=payload,
    )

    return response
