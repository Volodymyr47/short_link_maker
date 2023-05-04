import sqlalchemy as sa
from aiopg.sa import create_engine
from datetime import datetime
import os

import config


metadata = sa.MetaData()

DB_LOCAL = f'postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWD}@localhost:5432/slm_db'
DB_URL = os.environ.get("DATABASE_URL", DB_LOCAL)

tbl_link = sa.Table('tbl_link', metadata,
                    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('old_link', sa.String(255)),
                    sa.Column('new_link', sa.String(255)),
                    sa.Column('user_id', sa.Integer, nullable=True),
                    sa.Column('created', sa.DATETIME, default=datetime.utcnow()))


async def init_db():
    try:
        connection = await create_engine(DB_URL)
        return connection
    except Exception as err:
        print(err)


async def insert_one(tablename, **kwargs):
    try:
        engine = await init_db()
        async with engine:
            async with engine.acquire() as conn:
                await conn.execute(tablename.insert().values(**kwargs))
                return True
    except Exception as err:
        print(f'Insert data error\n{err}')
        return False


async def select_one(tablename, link, user_id=None):
    try:
        engine = await init_db()
        async with engine:
            async with engine.acquire() as conn:
                if not user_id:
                    raw_result = await conn.execute(tablename.select().where(tablename.c.new_link == link))
                    result = await raw_result.fetchone()
                    return result[1]
                raw_result = await conn.execute(tablename.select().where(tablename.c.new_link == link,
                                                                         tablename.c.new_link == user_id))
                result = await raw_result.fetchone()
                return result[1]
    except Exception as err:
        print(f'Select_data ERROR \n{err}')


async def select_many(tablename, user_id):
    try:
        engine = await init_db()
        async with engine.acquire() as conn:
            raw_result = await conn.execute(tablename.select().where(tablename.c.user_id == user_id))
            raw_result = await raw_result.fetchall()
            result = [f'{config.SLM_HOST}:80/{result[2]} --> {result[1]}' for result in raw_result]
            return result
    except Exception as err:
        print(f'Select_data ERROR \n{err}')
