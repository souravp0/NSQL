from db_connectors import PostgresConnector
from model_loader import generateQueryUsingSqlCoder
from prompt_formatters import RajkumarFormatter
from manifest import Manifest
from flask import Flask, request
import json

application = Flask(__name__)


class Temp:
    def __init__(self):
        USER = 'gpt_user'
        PASSWORD = 'gpt-dd-2023'
        DATABASE = 'postgres'
        HOST = 'database-2-enc.cq07lm9jlti9.us-east-2.rds.amazonaws.com'
        PORT = 5432
        SCHEMA = 'flecso'
        self.postgres_connector = PostgresConnector(
            user=USER, password=PASSWORD, dbname=DATABASE, host=HOST, port=PORT, search_schema=SCHEMA)
        self.postgres_connector.connect()

        all_tables = self.postgres_connector.get_tables()
        all_views = self.postgres_connector.get_views()
        all_tables_views = all_tables + all_views

        if self.table_filter != [] and self.table_filter != None:
            final_tables = [value for value in self.table_filter if value in all_tables_views]
        else:
            final_tables = all_tables_views

        db_schema = [self.postgres_connector.get_schema(table) for table in final_tables]
        self.formatter = RajkumarFormatter(db_schema)

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
    if USER is None:
        USER = 'gpt_user'
    PASSWORD = req['password']
    if PASSWORD is None:
        PASSWORD = 'gpt-dd-2023'
    DATABASE = req['db']
    if DATABASE is None:
        DATABASE = 'postgres'
    HOST = req['host']
    if HOST is None:
        HOST = 'database-2-enc.cq07lm9jlti9.us-east-2.rds.amazonaws.com'
    PORT = req['port']
    if PORT is None:
        PORT = 5432
    SCHEMA = req['schema']
    if SCHEMA is None:
        SCHEMA = 'flecso'

    temp.postgres_connector = PostgresConnector(
        user=USER, password=PASSWORD, dbname=DATABASE, host=HOST, port=PORT, search_schema=SCHEMA)
    temp.postgres_connector.connect()

    all_tables = temp.postgres_connector.get_tables()
    all_views = temp.postgres_connector.get_views()
    all_tables_views = all_tables + all_views

    if temp.table_filter != [] and temp.table_filter != None:
        final_tables = [value for value in temp.table_filter if value in all_tables_views]
    else:
        final_tables = all_tables_views

    db_schema = [temp.postgres_connector.get_schema(table) for table in final_tables]
    temp.formatter = RajkumarFormatter(db_schema)
    return "Connected!!"


def get_sql(instruction: str, max_tokens: int = 300) -> str:
    manifest_client = Manifest(client_name="huggingface", client_connection="localhost:5000")
    prompt = temp.formatter.format_prompt(instruction)
    res = manifest_client.run(prompt, max_tokens=max_tokens)
    return temp.formatter.format_model_output(res)


@application.route('/query', methods=['POST'])
def get_sql() -> dict:
    req = request.get_json()
    instruction = req['instruction']
    max_tokens = req['max_tokens']
    special_instructions = req['special_instructions']

    try:
        prompt = temp.formatter.format_prompt_sqlcoder(instruction, special_instructions)
        query = generateQueryUsingSqlCoder(prompt, max_tokens)
        res = {'query': query, 'prompt': prompt}
        return res

    except Exception as e:
        print(f"Got Exception {e=}, {type(e)=}")

@application.route('/queryDirect', methods=['POST'])
def get_sql() -> dict:
    req = request.get_json()
    prompt = req['prompt']
    max_tokens = req['max_tokens']

    try:
        query = generateQueryUsingSqlCoder(prompt, max_tokens)
        res = {'query': query, 'prompt': prompt}
        return res

    except Exception as e:
        print(f"Got Exception {e=}, {type(e)=}")

@application.route('/filterTables', methods=['POST'])
def filter_tables() -> str:
    req = request.get_json()
    filter_tables = req['tables']
    temp.table_filter = filter_tables

    if temp.postgres_connector is not None:
        all_tables = temp.postgres_connector.get_tables()
        all_views = temp.postgres_connector.get_views()
        all_tables_views = all_tables + all_views
        if temp.table_filter != [] and temp.table_filter is not None:
            final_tables = [value for value in temp.table_filter if value in all_tables_views]
        else:
            final_tables = all_tables_views

        db_schema = [temp.postgres_connector.get_schema(table) for table in final_tables]
        temp.formatter = RajkumarFormatter(db_schema)

    return json.dumps(temp.formatter.table_str)


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5003)
