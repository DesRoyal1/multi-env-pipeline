import boto3
import json
import os

def lambda_handler(event, context):
    environment = os.environ.get('ENVIRONMENT', 'dev')
    sns_topic = os.environ.get('SNS_TOPIC_ARN')
    api_function = os.environ.get('API_FUNCTION')

    lambda_client = boto3.client('lambda', region_name='us-east-1')
    sns = boto3.client('sns', region_name='us-east-1')

    print(f"Self-heal triggered for {environment} environment")

    try:
        # Test if API Lambda is responding
        response = lambda_client.invoke(
            FunctionName=api_function,
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'rawPath': '/health',
                'requestContext': {'http': {'method': 'GET'}},
                'headers': {},
                'rawQueryString': ''
            })
        )
        payload = json.loads(response['Payload'].read())
        status_code = payload.get('statusCode', 500)
        healed = status_code == 200
        heal_status = f"Health check returned {status_code}"
    except Exception as e:
        healed = False
        heal_status = f"Health check failed: {str(e)}"

    message = f"""
INCIDENT DETECTED — {environment.upper()} ENVIRONMENT

Function: {api_function}
Heal Result: {heal_status}
Status: {"Healthy" if healed else "Degraded"}

{"System is responding normally" if healed else "Manual investigation may be required"}
    """

    try:
        sns.publish(
            TopicArn=sns_topic,
            Subject=f'Incident Alert: {environment.upper()} Lambda',
            Message=message
        )
    except Exception as e:
        print(f"SNS publish failed: {str(e)}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'environment': environment,
            'healed': healed,
            'status': heal_status
        })
    }
