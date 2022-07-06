from datetime import datetime

from pydantic import BaseModel, HttpUrl


class EventDates(BaseModel):
    start: datetime
    end: datetime


class EventLogo(BaseModel):
    src: HttpUrl
    alt: str = "N/A"


class EventAddress(BaseModel):
    city: str = "N/A"
    state: str = "N/A"
    region: str = "N/A"


class HackathonEvent(BaseModel):
    title: str
    website: HttpUrl
    date: EventDates
    logo: EventLogo
