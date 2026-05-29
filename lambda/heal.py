import boto3
import json
import os
import urllib.request

def lambda_handler(event, context):
    environment = os.environ.get('ENVIRONMENT', 'prod')
    cluster = f'multi-env-{environment}'
    service = f'multi-env-{environment}'
    sns_topic = os.environ.get('SNS_TOPIC_ARN')
    
    ecs = boto3.client('ecs', region_name='us-east-1')
    sns = boto3.client('sns', region_name='us-east-1')
    
    print(f"Incident detected for {environment} environment")
    
    # Step 1 — attempt self healing
    try:
        print("Attempting self-heal: forcing new deployment...")
        ecs.update_service(
            cluster=cluster,
            service=service,
            forceNewDeployment=True
        )
        heal_status = "Self-heal initiated: forcing new ECS deployment"
        healed = True
    except Exception as e:
        heal_status = f"Self-heal failed: {str(e)}"
        healed = False
    
    # Step 2 — get current service status
    try:
        response = ecs.describe_services(
            cluster=cluster,
            services=[service]
        )
        svc = response['services'][0]
        running = svc['runningCount']
        desired = svc['desiredCount']
        status = svc['status']
    except Exception as e:
        running = 0
        desired = 0
        status = 'UNKNOWN'

    # Step 3 — send alert
    message = f"""
🚨 INCIDENT DETECTED — {environment.upper()} ENVIRONMENT

Status: {status}
Running Tasks: {running}/{desired}
Heal Attempt: {heal_status}

Cluster: {cluster}
Service: {service}
Region: us-east-1

{"✅ Self-heal initiated — monitor for recovery" if healed else "❌ Manual intervention required"}

View in AWS Console:
https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/{cluster}/services/{service}
    """
    
    try:
        sns.publish(
            TopicArn=sns_topic,
            Subject=f'🚨 Incident Alert: {environment.upper()} is DOWN',
            Message=message
        )
        print("Alert sent successfully")
    except Exception as e:
        print(f"Failed to send alert: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'environment': environment,
            'healed': healed,
            'heal_status': heal_status,
            'running_tasks': running
        })
    }
