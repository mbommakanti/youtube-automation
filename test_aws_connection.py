import boto3
import os
from datetime import datetime

def test_aws_connection():
    """Test AWS connection on Windows"""
    try:
        print("🔍 Testing AWS connection...")
        
        # Test EventBridge
        events_client = boto3.client('events', region_name='us-east-1')
        rules = events_client.list_rules()
        print(f"✅ EventBridge: Connected successfully")
        
        # Test Lambda
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        functions = lambda_client.list_functions()
        print(f"✅ Lambda: Connected successfully")
        
        # Test DynamoDB
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        tables = dynamodb.list_tables()
        print(f"✅ DynamoDB: Connected successfully")
        
        print(f"✅ All AWS services accessible from Windows!")
        return True
        
    except Exception as e:
        print(f"❌ AWS connection failed: {e}")
        print("💡 Check your AWS credentials with: aws configure list")
        return False

if __name__ == "__main__":
    test_aws_connection()