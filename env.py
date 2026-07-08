import os
from dotenv import load_dotenv 

def get_credentials():
    creds = {}
    
    # Load environment variables from .env file if not already loaded
    if not os.environ.get('aws_access_key_id'):
        env_file_dir = os.path.dirname(os.path.abspath(__file__))
        load_dotenv(os.path.join(env_file_dir, '.env'))
    
    # Fetch credentials from environment variables
    creds['aws_access_key_id'] = os.environ.get('aws_access_key_id')
    creds['region_name'] = os.environ.get('region_name')
    creds['aws_secret_access_key'] = os.environ.get('aws_secret_access_key')
    creds['aws_session_token'] = os.environ.get('aws_session_token')
    creds['account_id'] = os.environ.get('account_id')
    creds['base_url'] = os.environ.get('base_url')
    creds['iss'] = os.environ.get('iss')
    creds['sub'] = os.environ.get('sub')
    creds['api_url']=os.environ.get('api_url')
    creds['email']=os.environ.get('email')
    creds['password']=os.environ.get('password')
    creds['smtp_host']=os.environ.get('smtp_host')
    creds['smtp_port']=os.environ.get('smtp_port')
    creds['smtp_username'] = os.environ.get('smtp_username')
    creds['smtp_password'] = os.environ.get('smtp_password')
    creds['sender'] = os.environ.get('sender')
    creds['aws_access_key_id1'] = os.environ.get('aws_access_key_id1')
    creds['aws_secret_access_key1'] = os.environ.get('aws_secret_access_key1')
    creds['fbase_url']=os.environ.get('fbase_url')


    return creds

credentials = get_credentials() 