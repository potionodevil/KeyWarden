from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.engine import Result
from sqlalchemy import insert, select, delete, update
from dotenv import dotenv_values

class Core:
    def __init__(self):
        env = dotenv_values(".env")
        self.engine = create_engine(
            f"mysql+mysqlconnector://{env['DB_USER']}:{env['DB_PASSWORD']}@{env['DB_HOST']}:{env['DB_PORT']}/?charset=utf8"
        )
        self.connection = self.engine.connect()
        self.mapper = MetaData()
        self.users = Table("users", self.mapper,
                           Column("id", Integer, primary_key=True),
                           Column("name", String(50)),
                           Column("email", String(50)),
                           Column("password", String(50)),
                           Column("2fa", Boolean),
                           Column("Adress", String(50)),
                           Column("reset_code", String(100)))


class StatementBuilder:

    def __init__(self, table, connection):
        self.table = table
        self.statement = None
        self.connection = connection


    def check_connection(self):
        if(not self.connection):
            return False
        else:
            return True

    def insert(self, data: dict):
        self.statement = insert(self.table).values(**data)
        return self

    def select(self, **where):
        if where:
            conditions = [self.table.c[k] == v for k, v in where.items()]
            self.statement = select(self.table).where(*conditions)
        else:
            self.statement = select(self.table)
        return self

    def update(self, set_values: dict, **where):
        conditions = [self.table.c[k] == v for k, v in where.items()]
        self.statement = update(self.table).where(*conditions).values(**set_values)
        return self

    def delete(self, **where):
        conditions = [self.table.c[k] == v for k, v in where.items()]
        self.statement = delete(self.table).where(*conditions)
        return self

    def build(self):
        return str(self.statement), self.statement.compile().params

    def execute(self, conn=None, as_dict=False):
        if not conn:
            conn = self.connection
        result = conn.execute(self.statement)
        if as_dict:
            return [dict(row._mapping) for row in result]
        return result

class QueryResultWrapper:

    def __init__(self, result):
        self.result = result
        self.rows = list(result)

    def first(self):
        return self.rows[0] if self.rows else None

    def all(self):
        return self.rows

    def first_dict(self):
        row = self.first()
        return dict(row._mapping) if row else None

    def all_dict(self):
        return [dict(row._mapping) for row in self.all()]

    def to_json(self):
        import json
        return json.dumps(self.all_dict(), indent=2)

