from os import path
import json
from sqlmodel.ext.asyncio.session import AsyncSession

from database import engine
from dbmodel.model import Model
from dbmodel.category import Category
from dbmodel.overlappingcategory import OverlappingCategory


async def store_models(dirname: str) -> bool:
    f_category = path.join(dirname, 'categories.json')
    if not path.exists(f_category):
        print('File categories.json was not found.')
        return None, False

    with open(f_category, 'r') as fp:
        model_list: dict = json.load(fp)

    session: AsyncSession = AsyncSession(engine)

    async with session:
        for model in model_list:
            print(f'Model: {model["name"]}, descr: {model["descr"]}')

            print(json.dumps(model["categories"], indent=3))

            newmodel = Model(name=model.get("name"), descr=model.get("descr"))
            session.add(newmodel)
        await session.commit()
        await session.close()

    return