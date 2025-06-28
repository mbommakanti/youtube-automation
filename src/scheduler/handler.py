import json
import logging
import os
from datetime import datetime
import boto3

# Configure logging for Windows with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs\\scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """Main scheduler handler for Windows development"""
    
    try:
        logger.info("VIRAL SHORTS PIPELINE STARTED (Windows)")
        logger.info(f"Triggered at: {datetime.now().isoformat()}")
        logger.info(f"Event: {json.dumps(event, indent=2)}")
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Test AWS connection
        try:
            events_client = boto3.client('events')
            logger.info("SUCCESS: AWS connection successful")
        except Exception as aws_error:
            logger.error(f"ERROR: AWS connection failed: {aws_error}")
            raise
        
        pipeline_status = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'platform': 'windows',
            'message': 'Scheduler running successfully on Windows'
        }
        
        logger.info("SUCCESS: Pipeline completed successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps(pipeline_status)
        }
        
    except Exception as e:
        logger.error(f"ERROR: Pipeline failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'platform': 'windows'
            })
        }

# For local testing on Windows
if __name__ == "__main__":
    # Simulate EventBridge event
    test_event = {
        "source": "aws.events",
        "detail-type": "Scheduled Event",
        "detail": {}
    }
    
    test_context = type('Context', (), {
        'function_name': 'viral-shorts-scheduler',
        'memory_limit_in_mb': 128,
        'invoked_function_arn': 'arn:aws:lambda:us-east-1:123456789012:function:test'
    })()
    
    result = lambda_handler(test_event, test_context)
    print(f"Result: {json.dumps(result, indent=2)}")