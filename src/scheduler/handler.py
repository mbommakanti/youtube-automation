import json
import logging
import os
from datetime import datetime
import boto3
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config import Config

def setup_logging():
    """Configure logging based on configuration settings"""
    config = Config.get_instance()
    
    # Create log folder if needed (local environment)
    if config.should_create_log_folder and config.log_file_path:
        from pathlib import Path
        log_path = Path(config.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get handlers based on configuration
    handlers = []
    
    if config.log_handler == 'file' and config.log_file_path:
        # File handler for local development
        handlers.append(logging.FileHandler(config.log_file_path, encoding='utf-8'))
    
    if config.log_handler == 'console' or config.environment == 'production':
        # Console handler (always include for production/Lambda)
        handlers.append(logging.StreamHandler())
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Override any existing configuration
    )

# Initialize configuration and logging
setup_logging()
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """Main scheduler handler with configuration-based setup"""
    
    config = Config.get_instance()
    
    try:
        logger.info("VIRAL SHORTS PIPELINE STARTED")
        logger.info(f"Environment: {config.environment}")
        logger.info(f"Triggered at: {datetime.now().isoformat()}")
        logger.info(f"Event: {json.dumps(event, indent=2)}")
        
        # Get AWS configuration from config system
        aws_region = config.get_config_value('aws.region', 'us-east-1')
        timeout = config.get_config_value('aws.timeout', 30)
        
        # Test AWS connection with configured settings
        try:
            events_client = boto3.client('events', region_name=aws_region)
            logger.info("SUCCESS: AWS connection successful")
            logger.debug(f"AWS region: {aws_region}, timeout: {timeout}")
        except Exception as aws_error:
            logger.error(f"ERROR: AWS connection failed: {aws_error}")
            raise
        
        # Get pipeline configuration
        max_retries = config.get_config_value('pipeline.max_retries', 3)
        batch_size = config.get_config_value('pipeline.batch_size', 10)
        
        pipeline_status = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'environment': config.environment,
            'config': {
                'max_retries': max_retries,
                'batch_size': batch_size,
                'aws_region': aws_region
            },
            'message': f'Scheduler running successfully in {config.environment} environment'
        }
        
        logger.info("SUCCESS: Pipeline completed successfully")
        logger.debug(f"Pipeline config: retries={max_retries}, batch_size={batch_size}")
        
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
                'environment': config.environment
            })
        }

# For local testing
if __name__ == "__main__":
    # Set environment for testing (if not already set)
    if 'APP_ENV' not in os.environ:
        os.environ['APP_ENV'] = 'local'
    
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
    
    print("Testing with configuration system...")
    config = Config.get_instance()
    print(f"Environment: {config.environment}")
    print(f"Log level: {config.log_level}")
    print(f"Log handler: {config.log_handler}")
    
    result = lambda_handler(test_event, test_context)
    print(f"Result: {json.dumps(result, indent=2)}")