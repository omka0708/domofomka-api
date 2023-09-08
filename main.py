import sqlite3
import re
import os

from fastapi import FastAPI, Query
from typing import Annotated
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = FastAPI()


def regexp(value, pattern):
    return re.compile(pattern.lower()).search(value.lower()) is not None


def get_data(msg, db_name):
    pattern = '^.*' + '.* '.join(msg.split()) + '$'
    res = {}
    with sqlite3.connect(os.getenv('DB_NAME')) as connection:
        cursor = connection.cursor()
        connection.create_function("regexp", 2, regexp)
        query_find_first = f"select address from {db_name} where regexp ({db_name}.address, '{pattern}') limit 1"
        cursor.execute(query_find_first)
        address = cursor.fetchone()
        if address:
            address = address[0]
            query_find_all = f"select entrance, code from {db_name} where {db_name}.address == '{address}'"
            cursor.execute(query_find_all)
            data = cursor.fetchall()
            if data:
                res['address'] = address
                for ent, code in data:
                    res.setdefault('data', {})
                    res['data'].setdefault(ent, []).append(code)
    return res


@app.get("/codes")
async def get_codes_by_message(message: Annotated[str, Query(min_length=7, max_length=50)]):
    result = {'yaeda': get_data(message, 'yaeda'),
              'delivery': get_data(message, 'delivery'),
              'oldcodes': get_data(message, 'oldcodes')}
    return result
