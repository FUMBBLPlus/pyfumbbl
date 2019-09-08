import copy
import json
import uuid

from pyfumbbl._session import with_default_session
from pyfumbbl import exc
from pyfumbbl import group

__all__ = [
    'get',
    'schedule',
  ]

styles = (
    'Knockout',  # 1
    'Round Robin',  # 2
    'Open Round Robin',  # ...
    'Swiss',
    'King of the Hill',
)

progressions = (
    'Standard',  # 1
    'None',  # 2
)


@exc.returns_api_error_checked_result
@with_default_session
def get_data(tournament_id, session=None):
  """Returns a tournaments data."""
  tournament_id = str(tournament_id)
  assert tournament_id.isdecimal()
  url = session.baseurl / f'api/tournament/get/{tournament_id}'
  r = session.get(url).json()
  return r


get = get_data


@exc.returns_api_error_checked_result
@with_default_session
def get_schedule(tournament_id, session=None):
  tournament_id = str(tournament_id)
  assert tournament_id.isdecimal()
  url = session.baseurl / 'api/tournament/schedule'
  url = url / str(tournament_id)
  r = session.get(url)
  return r.json()


schedule = get_schedule
