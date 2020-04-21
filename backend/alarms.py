from typing import List

import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

alarms = sqlalchemy.Table(
    "alarms",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("twilio_key", sqlalchemy.String),
    sqlalchemy.Column("twilio_sid", sqlalchemy.String),
    sqlalchemy.Column("ameritrade_key", sqlalchemy.String),
    sqlalchemy.Column("from_phone", sqlalchemy.String),
    sqlalchemy.Column("to_phones", sqlalchemy.String),
    sqlalchemy.Column("indicator", sqlalchemy.String),
    sqlalchemy.Column("kcband", sqlalchemy.String),
    sqlalchemy.Column("crossingType", sqlalchemy.String),
    sqlalchemy.Column("averageType", sqlalchemy.String),
    sqlalchemy.Column("trueRangeAverageType", sqlalchemy.String),
    sqlalchemy.Column("price", sqlalchemy.String),
    sqlalchemy.Column("displace", sqlalchemy.Integer),
    sqlalchemy.Column("factor", sqlalchemy.Integer),
    sqlalchemy.Column("length", sqlalchemy.Integer),
    sqlalchemy.Column("sms", sqlalchemy.Boolean),
    sqlalchemy.Column("phone_call", sqlalchemy.Boolean),
    sqlalchemy.Column("status", sqlalchemy.String),
)


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


class AlarmIn(BaseModel):
    title: str
    twilio_key: str
    twilio_sid: str
    ameritrade_key: str
    from_phone: str
    to_phones: str
    indicator: str
    kcband: str
    crossingType: str
    price: str
    averageType: str
    trueRangeAverageType: str
    displace: int
    factor: int
    length: int
    sms: bool
    phone_call: bool
    status: str


class Alarm(BaseModel):
    id: int
    title: str
    twilio_key: str
    twilio_sid: str
    ameritrade_key: str
    from_phone: str
    to_phones: str
    indicator: str
    kcband: str
    crossingType: str
    price: str
    averageType: str
    trueRangeAverageType: str
    displace: int
    factor: int
    length: int
    sms: bool
    phone_call: bool
    status: str


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/alarms/", response_model=List[Alarm])
async def read_alarms():
    query = alarms.select()
    return await database.fetch_all(query)


@app.post("/alarm/", response_model=Alarm)
async def create_alarm(alarm: AlarmIn):
    query = alarms.insert().values(
        title=alarm.title,
        twilio_key=alarm.twilio_key,
        twilio_sid=alarm.twilio_sid,
        ameritrade_key=alarm.ameritrade_key,
        from_phone=alarm.from_phone,
        to_phones=alarm.to_phones,
        indicator=alarm.indicator,
        kcband=alarm.kcband,
        crossingType=alarm.crossingType,
        displace=alarm.displace,
        factor=alarm.factor,
        length=alarm.length,
        price=alarm.price,
        averageType=alarm.averageType,
        trueRangeAverageType=alarm.trueRangeAverageType,
        sms=alarm.sms,
        phone_call=alarm.phone_call,
        status=alarm.status)
    last_record_id = await database.execute(query)
    return {**alarm.dict(), "id": last_record_id}

@app.delete("/alarm/{id}")
async def delete_alarm(id):
    deleted_record_res = await database.execute('DELETE from "alarms" where id='+id+';')
    return {"success": deleted_record_res}


@app.post("/start_alarm/", response_model=Alarm)
async def start_alarm(alarm: AlarmIn):
    import ipdb; ipdb.set_trace()
    pass