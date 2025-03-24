import json
import boto3
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_aws_session():
    """Create and return an AWS session using environment credentials"""
    # Boto3 will automatically use AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and 
    # AWS_SESSION_TOKEN environment variables if they are set
    return boto3.Session(region_name=settings.AWS_REGION)

def send_appointment_notification(appointment):
    """Send appointment notification via SNS"""
    try:
        session = get_aws_session()
        sns_client = session.client('sns')
        
        # Format appointment data for the notification
        appointment_data = {
            'appointment_id': appointment.id,
            'title': appointment.title,
            'name': appointment.name,
            'email': appointment.email,
            'phone': appointment.phone,
            'appointment_type': appointment.get_appointment_type_display(),
            'date_time': appointment.date_time.isoformat(),
            'duration': appointment.duration,
            'description': appointment.description
        }
        
        # Publish message to SNS topic
        response = sns_client.publish(
            TopicArn=settings.AWS_SNS_TOPIC_ARN,
            Message=json.dumps(appointment_data),
            Subject=f"New Appointment: {appointment.title}",
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': appointment.email
                },
                'appointment_type': {
                    'DataType': 'String',
                    'StringValue': appointment.appointment_type
                }
            }
        )
        logger.info(f"SNS notification sent successfully. MessageId: {response.get('MessageId')}")
        return response
    except Exception as e:
        logger.error(f"Error sending SNS notification: {str(e)}")
        raise

def invoke_lambda_for_appointment(appointment):
    """Invoke Lambda function with appointment data"""
    try:
        session = get_aws_session()
        lambda_client = session.client('lambda')
        
        # Format appointment data for Lambda
        payload = {
            'appointment_id': appointment.id,
            'title': appointment.title,
            'name': appointment.name,
            'email': appointment.email,
            'phone': appointment.phone,
            'appointment_type': appointment.get_appointment_type_display(),
            'date_time': appointment.date_time.isoformat(),
            'duration': appointment.duration,
            'description': appointment.description
        }
        
        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName=settings.AWS_LAMBDA_FUNCTION_ARN,
            InvocationType='Event',  # Asynchronous invocation
            Payload=json.dumps(payload)
        )
        
        logger.info(f"Lambda function invoked successfully. StatusCode: {response.get('StatusCode')}")
        return response
    except Exception as e:
        logger.error(f"Error invoking Lambda function: {str(e)}")
        raise

def get_s3_client():
    """Create and return an S3 client using environment credentials"""
    session = get_aws_session()
    return session.client('s3')

def upload_file_to_s3(file_obj, filename, content_type=None):
    """
    Upload a file to the S3 bucket
    
    Args:
        file_obj: File-like object to upload
        filename: Name to save the file as in S3
        content_type: MIME type of the file (optional)
    
    Returns:
        URL of the uploaded file
    """
    try:
        s3_client = get_s3_client()
        bucket_name = 'appointment-images-bucket'
        
        # Set extra arguments for the upload
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        # Upload the file
        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            filename,
            ExtraArgs=extra_args
        )
        
        # Generate the URL for the file
        region = settings.AWS_REGION
        url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"
        
        logger.info(f"File uploaded successfully to S3: {url}")
        return url
    except Exception as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        raise

def get_s3_file_url(filename):
    """
    Get the URL for a file in S3
    
    Args:
        filename: Name of the file in S3
    
    Returns:
        URL of the file
    """
    bucket_name = 'appointment-images-bucket'
    region = settings.AWS_REGION
    return f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"

def delete_file_from_s3(filename):
    """
    Delete a file from the S3 bucket
    
    Args:
        filename: Name of the file to delete
    """
    try:
        s3_client = get_s3_client()
        bucket_name = 'appointment-images-bucket'
        
        # Delete the file
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=filename
        )
        
        logger.info(f"File deleted successfully from S3: {filename}")
    except Exception as e:
        logger.error(f"Error deleting file from S3: {str(e)}")
        raise

def list_files_in_s3():
    """
    List all files in the S3 bucket
    
    Returns:
        List of filenames
    """
    try:
        s3_client = get_s3_client()
        bucket_name = 'appointment-images-bucket'
        
        # List objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        # Extract filenames
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append(obj['Key'])
        
        return files
    except Exception as e:
        logger.error(f"Error listing files in S3: {str(e)}")
        raise