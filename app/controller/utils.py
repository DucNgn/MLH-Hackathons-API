import pendulum

from app.config import get_settings


def get_today():
    settings = get_settings()
    now = pendulum.now(settings.TIMEZONE)
    return now
