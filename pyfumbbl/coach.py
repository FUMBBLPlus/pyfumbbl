import copy
import json
from xml.etree import ElementTree

from pyfumbbl import _helper
from pyfumbbl._session import with_default_session
from pyfumbbl import exc

__all__ = [
    'get',
    'search',
    'get_teams',
  ]

@exc.returns_api_error_checked_result
@with_default_session
def get_data(coach_id, *, session=None):
  """Returns a coach's data."""
  coach_id = str(coach_id)
  assert coach_id.isdecimal()
  url = session.baseurl / f'api/coach/get/{coach_id}'
  r = session.get(url).json()
  return r


get = get_data


@exc.returns_api_error_checked_result
@with_default_session
def get_search(term, *, session=None):
  """Search for a coach"""
  url = session.baseurl / f'api/coach/search/{term}'
  r = session.get(url).json()
  return r


search = get_search


@exc.returns_api_error_checked_result
@with_default_session
def get_teams(coach, *, session=None):
  """Returns a list of the teams of the given coach (name)."""
  url = session.baseurl / f'api/coach/teams/{coach}'
  r = session.get(url).json()
  return r
