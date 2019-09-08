import copy
import json
import re
import warnings

from pyfumbbl._session import with_default_session
from pyfumbbl import exc
from pyfumbbl.division import division

import yarl

__all__ = [
  'current',
  'get',
  'get_legacy_data',
  'get_list',
  ]


@exc.returns_api_error_checked_result
@with_default_session
def get_current(session=None):
  """Return the data of currently running matches."""
  url = session.baseurl / 'api/match/current'
  r = session.get(url)
  return r.json()


current = get_current


@exc.returns_api_error_checked_result
@with_default_session
def get_data(match_id, session=None):
  """Returns a match data."""
  match_id = str(match_id)
  assert match_id.isdecimal()
  url = session.baseurl / f'api/match/get/{match_id}'
  r = session.get(url).json()
  return r


get = get_data


@exc.returns_api_error_checked_result
@with_default_session
def get_legacy_data(match_id, session=None):
  """Returns a raw legacy match XML data string."""
  match_id = str(match_id)
  assert match_id.isdecimal()
  url = session.baseurl / f'xml:matches'
  r = session.get(url, params={"m": match_id}).text
  return r


@with_default_session
def get_list_data(starting=None, session=None):
  """Return the list of matches."""
  url = session.baseurl / 'api/match/list'
  if starting is not None:
    starting = int(starting)
  url = url / str(starting)
  r = session.get(url)
  return r.json()


get_list = get_list_data
