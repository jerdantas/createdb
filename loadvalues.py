import base64
import json
from os import path
from sqlmodel.ext.asyncio.session import AsyncSession
from urllib.parse import urlparse
from passlib.hash import pbkdf2_sha256 as crypt

import settings
from database import engine
from dbmodel.customer import Customer
from dbmodel.camera import Camera
from dbmodel.category import Category
from dbmodel.overlappingcategory import OverlappingCategory
from dbmodel.event import Event
from dbmodel.rule import Rule
from dbmodel.alarm import Alarm
from dbmodel.bbox import Bbox
from dbmodel.user import User

from lex.token_type import TokenType
from lex.scanner import Scanner
from analyse import AnalyseRule

# Data to read must be in same directory as the database
dburl = urlparse(settings.DB_CONNECTION_STR)
dirname = path.dirname(dburl.path)


async def store_customer():
    f_customer = path.join(dirname, 'customer.json')
    with open(f_customer, 'r') as fp:
        customers = json.load(fp)

    session: AsyncSession = AsyncSession(engine)

    async with session:
        for cust in customers:
            new_cust: Customer = Customer(**cust)
            session.add(new_cust)
        await session.commit()
        await session.close()


def set_user_pw(password: str) -> str:
    cript_password = crypt.hash(password)
    return cript_password

async def store_user():
    f_user = path.join(dirname, 'user.json')
    with open(f_user, 'r') as fp:
        users = json.load(fp)

    session: AsyncSession = AsyncSession(engine)

    async with session:
        for user in users:
            new_user: User = User(**user)
            new_user.password = set_user_pw(new_user.password)
            session.add(new_user)
        await session.commit()
        await session.close()


async def store_camera():
    f_camera = path.join(dirname, 'camera.json')
    with open(f_camera, 'r') as fp:
        cameras = json.load(fp)

    session: AsyncSession = AsyncSession(engine)

    async with session:
        for cam in cameras:
            new_cam: Camera = Camera(**cam)
            session.add(new_cam)
        await session.commit()
        await session.close()


async def store_yolo_classes():
    f_classes = path.join(dirname, 'classes.json')
    with open(f_classes, 'r') as fp:
        classes: dict = json.load(fp)

    session: AsyncSession = AsyncSession(engine)

    async with session:
        for k in classes.keys():
            new_cat = Category(id=int(k), name=classes[k], min_area=0)
            session.add(new_cat)
        await session.commit()
        await session.close()


async def store_category() -> (dict[str, int], bool):
    f_category = path.join(dirname, 'categories.txt')
    if not path.exists(f_category):
        print('File categories_new.txt was not found.')
        return None, False

    cat_list = {}
    file = open(f_category, mode='r', encoding='utf-8')
    lines = file.readlines()
    line_no = 1

    session: AsyncSession = AsyncSession(engine)

    async with session:

        for line in lines:
            scan = Scanner(line)

            token = scan.next_token()
            if token.token_type != TokenType.INT:
                print(f'Categories file: Line should start with an integer line {line_no} col {token.col}.')
                return None, False
            category_id = int(token.text)

            token = scan.next_token()
            if token.token_type != TokenType.WORD:
                print(f'Categories file: Expected category name on line {line_no} col {token.col}.')
                return None, False
            category_name = token.text
            cat_list[category_name] = category_id

            token = scan.next_token()
            if token.token_type != TokenType.REAL:
                print(f'Categories file: Invalid area specification on line {line_no} col {token.col}.')
                return None, False
            category_area = float(token.text)

            new_cat = Category(id=category_id, name=category_name, min_area=category_area)
            session.add(new_cat)

            token = scan.next_token()
            while token.token_type != TokenType.EOT:
                if token.token_type != TokenType.WORD:
                    print(f'Categories file: Expected category overlapping name on line {line_no} col {token.col}.')
                    return None, False
                overlapping_id = cat_list[token.text]

                token = scan.next_token()
                if token.token_type != TokenType.INT:
                    print(f'Categories file: Expected overlapping position on line {line_no} col {token.col}.')
                    return None, False
                over_position = int(token.text)

                token = scan.next_token()
                if token.token_type != TokenType.REAL:
                    print(f'Categories file: Expected proportion on line {line_no} col {token.col}.')
                    return None, False
                proportion = float(token.text)

                new_ovcat = OverlappingCategory(cat_id=category_id,
                                                cat_ov=overlapping_id,
                                                overlappingposition=over_position,
                                                proportion=proportion)
                session.add(new_ovcat)

                token = scan.next_token()

                await session.commit()

            line_no += 1

    return cat_list, True


async def store_rules(cat_list: dict[str, int]) -> bool:
    rules_file = path.join(dirname, 'rules.txt')
    file = open(rules_file, mode='r', encoding='utf-8')
    lines = file.readlines()
    errors = 0
    lineno = 1

    session: AsyncSession = AsyncSession(engine)

    async with session:
        for line in lines:
            rule = AnalyseRule(line, lineno, cat_list)

            if rule.analyse():
                new_rule = Rule(name=rule.name,
                                category_name=rule.category_name,
                                expression=rule.rule_def)
                session.add(new_rule)
                await session.commit()
            else:
                errors += 1
            lineno += 1

    return errors == 0


async def store_event():
    f_event = path.join(dirname, 'event.json')
    if not path.exists(f_event):
        return
    with open(f_event, 'r') as fp:
        events = json.load(fp)

    session: AsyncSession = AsyncSession(engine)

    async with session:
        for event in events:
            l1 = len(event['image'])
            event['image'] = base64.b64decode(event['image'])
            l2 = len(event['image'])
            new_evnt: Event = Event(**event)
            session.add(new_evnt)
        await session.commit()
        await session.close()


async def store_bbox():
    f_bbox = path.join(dirname, 'bbox.json')
    if not path.exists(f_bbox):
        return
    with open(f_bbox, 'r') as fp:
        bboxes = json.load(fp)

    session: AsyncSession = AsyncSession(engine)

    async with session:
        for box in bboxes:
            new_box: Bbox = Bbox(**box)
            session.add(new_box)
        await session.commit()
        await session.close()


async def store_alarm():
    f_alarm = path.join(dirname, 'alarm.json')
    if not path.exists(f_alarm):
        return
    with open(f_alarm, 'r') as fp:
        alarms = json.load(fp)

    session: AsyncSession = AsyncSession(engine)

    async with session:
        for alarm in alarms:
            new_alarm: Alarm = Alarm(**alarm)
            session.add(new_alarm)
        await session.commit()
        await session.close()


async def load_data():
    await store_customer()
    await store_user()
    await store_camera()

    # await store_yolo_classes()
    # exit()

    # Populates category_index table
    cat_list, result = await store_category()
    if not result:
        return 1

    # fill rules table
    if not await store_rules(cat_list):
        return 1

    await store_event()
    await store_bbox()
    await store_alarm()

    print(f'Dados carregados de {dirname}.')
