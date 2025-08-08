import boto3
import time
import json

ATHENA_DB = 'pizzachain-rds-tbsm-db'
ATHENA_OUTPUT = 's3://tbsm-core/output/'
SQS_QUEUE_URL = 'https://sqs.ap-southeast2.amazonaws.com/008673239246/tbsm-pizza'

athena = boto3.client('athena')
sqs = boto3.client('sqs')


def run_athena_query(query):
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': ATHENA_DB},
        ResultConfiguration={'OutputLocation': ATHENA_OUTPUT}
    )
    query_execution_id = response['QueryExecutionId']
    
    while True:
        result = athena.get_query_execution(QueryExecutionId=query_execution_id)
        state = result['QueryExecution']['Status']['State']
        
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(2)
    
    if state != 'SUCCEEDED':
        reason = result['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
        raise Exception(f"Athena query failed: {state} - {reason}")
    
    return query_execution_id


def parse_results(query_execution_id):
    result = athena.get_query_results(QueryExecutionId=query_execution_id)
    rows = result['ResultSet']['Rows']
    headers = [col['VarCharValue'] for col in rows[0]['Data']]
    data = []
    
    for row in rows[1:]:
        values = [col.get('VarCharValue', '') for col in row['Data']]
        data.append(dict(zip(headers, values)))
    
    return data


def send_to_sqs(message):
    response = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(message)
    )
    return response


def lambda_handler(event, context):
    # Simple query to fetch any one record from pizzadb_stores
    test_query = """
    SELECT store_id, email
    FROM pizzadb_stores
    LIMIT 1;
    """
    
    # Run the query
    query_execution_id = run_athena_query(test_query)
    print("Athena QueryExecutionId:", query_execution_id)
    
    # Parse results
    result_data = parse_results(query_execution_id)
    print("Parsed Athena Results:", result_data)
    
    if not result_data:
        print("No records found in pizzadb_stores.")
        return {
            'statusCode': 200,
            'body': json.dumps('No records found.')
        }
    
    # Send the one record to SQS
    item = result_data[0]
    message = {
        'store_id': item.get('store_id'),
        'email': item.get('email'),
        'note': 'Test message from Lambda'
    }
    
    print("Sending to SQS:", message)
    response = send_to_sqs(message)
    print("SQS Send Response:", response)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Test record sent to SQS successfully.')
    }
