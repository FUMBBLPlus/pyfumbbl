import copy
import json
import warnings

from pyfumbbl._session import with_default_session
from pyfumbbl import exc

__all__ = [
    'get',
  ]


@exc.returns_api_error_checked_result
@with_default_session
def get_data(player_id, session=None):
  """Returns a player data."""
  player_id = str(player_id)
  assert player_id.isdecimal()
  url = session.baseurl / f'api/player/get/{player_id}'
  r = session.get(url).json()
  return r


get = get_data
