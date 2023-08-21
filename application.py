from db_connectors import PostgresConnector
from prompt_formatters import RajkumarFormatter
from sagemaker.huggingface.model import HuggingFacePredictor
from manifest import Manifest
from flask import Flask, request
import json

application = Flask(__name__)

class Temp:
    formatter = None
    table_filter = []
    postgres_connector = None

temp = Temp()

@application.route('/', methods=['GET'])
def index():
    return "Hello, World!"

@application.route('/connect', methods=['POST'])
def create_connection() -> str:
    req = request.get_json()
    USER = req['user']
    PASSWORD = req['password']
    DATABASE = req['db']
    HOST = req['host']
    PORT = req['port']
    SCHEMA = req['schema']

    postgres_connector = PostgresConnector(
        user=USER, password=PASSWORD, dbname=DATABASE, host=HOST, port=PORT, search_schema=SCHEMA)
    postgres_connector.connect()

    all_tables = postgres_connector.get_tables()
    all_views = postgres_connector.get_views()
    all_tables_views = all_tables + all_views

    if temp.table_filter != [] and temp.table_filter != None:
        final_tables = [value for value in temp.table_filter if value in all_tables_views]
    else:
        final_tables = all_tables_views

    db_schema = [postgres_connector.get_schema(table) for table in final_tables]
    temp.formatter = RajkumarFormatter(db_schema)
    return "Connected!!"

def get_sql(instruction: str, max_tokens: int = 300) -> str:
    manifest_client = Manifest(client_name="huggingface", client_connection="localhost:5000")
    prompt = temp.formatter.format_prompt(instruction)
    res = manifest_client.run(prompt, max_tokens=max_tokens)
    return temp.formatter.format_model_output(res)

@application.route('/query350M', methods=['POST'])
def get_sagemaker_sql_350M() -> str:
    req = request.get_json()
    instruction = req['instruction']
    max_tokens = req['max_tokens']
    prompt = temp.formatter.format_prompt(instruction)
    predictor = HuggingFacePredictor(endpoint_name="huggingface-pytorch-inference-2023-08-18-15-05-27-193")
    return predictor.predict({'inputs': prompt,
                  'parameters': {'max_length': max_tokens,
                                 'min_length': 1}})

@application.route('/query2B', methods=['POST'])
def get_sagemaker_sql_2B() -> str:
    req = request.get_json()
    instruction = req['instruction']
    max_tokens = req['max_tokens']
    prompt = temp.formatter.format_prompt(instruction)
    predictor = HuggingFacePredictor(endpoint_name="huggingface-pytorch-tgi-inference-2023-08-18-15-05-29-108")
    return predictor.predict({'inputs': prompt,
                  'parameters': {'max_length': max_tokens,
                                 'min_length': 1}})

@application.route('/filterTables', methods=['POST'])
def filter_tables() -> str:
    req = request.get_json()
    filter_tables = req['tables']
    temp.table_filter = filter_tables
    return json.dumps(temp.table_filter)

if __name__ == '__main__':
    application.run(port=5003)