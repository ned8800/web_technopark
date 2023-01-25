from django import template 
from app import models
import re
import humanfriendly
from datetime import datetime, timezone, timedelta

register = template.Library()

@register.filter(name = 'convert_date')
def convert_date(date):
    return re.split("(,| and)", humanfriendly.format_timespan(datetime.now(timezone.utc) - date))[0]