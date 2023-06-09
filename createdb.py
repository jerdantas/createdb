from os import path, remove
from sqlmodel import SQLModel
import asyncio

from database import engine
import dbmodel.__all_models
from loadvalues import load_data
import settings


async def create_tables() -> None:
    if path.exists(settings.DB_FILE_NAME):
        remove(settings.DB_FILE_NAME)
    print('Criando as tabelas no banco de dados...')
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        print('Drop all done')
        await conn.run_sync(SQLModel.metadata.create_all)
    print('Tabelas criadas com sucesso...')

    await load_data()


if __name__ == '__main__':
    asyncio.run(create_tables())
