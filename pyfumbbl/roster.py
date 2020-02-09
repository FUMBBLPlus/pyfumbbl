import copy
import json
from types import MappingProxyType
import warnings

from pyfumbbl._session import with_default_session
from pyfumbbl import exc
from pyfumbbl import position

__all__ = [
    'add',
    'add_star',
    'append_to_ruleset',
    'clone_to_ruleset',
    'create',
    'get',
    'remove',
    'remove_star',
    'search',
    'set_data',
  ]

_NO_DATA = {'positions': [], 'stars': []}

class NoRosterDataError(exc.NoDataError):
  pass


DEFAULT_LOGOS = MappingProxyType(dict((
    ('32', '486370'),
    ('48', '486369'),
    ('64', '486371'),
    ('96', '486372'),
    ('128', '486373'),
    ('192', '486374'),
)))


DETAILED_POSITIONS = 0b1
DETAILED_STARS = 0b10


def _rejuvenate(roster_data, _rejuvenate_positions=True,
    del_stars=False):
  if 'id' in roster_data:
    del roster_data['id']
  if 'positions' in roster_data and _rejuvenate_positions:
    for position_data in roster_data['positions']:
      position._rejuvenate(position_data)
  if 'stars' in roster_data and del_stars:
    for star_data in roster_data['stars']:
      if 'id' in star_data:
        del star_data['id']
  return roster_data


@exc.returns_api_error_checked_result
@with_default_session
def add(ruleset_id, roster_id, session=None):
  ruleset_id = str(ruleset_id)
  assert ruleset_id.isdecimal()
  roster_id = str(roster_id)
  assert roster_id.isdecimal()
  url = session.baseurl / 'api/roster/add'
  data = {'ruleset': ruleset_id, 'roster': roster_id}
  r = session.post(url, data=data)
  return r.json()


@exc.returns_api_error_checked_result
@with_default_session
def add_star(roster_id, position_id, session=None):
  roster_id = str(roster_id)
  assert roster_id.isdecimal()
  position_id = str(position_id)
  assert position_id.isdecimal()
  url = session.baseurl / f'api/roster/addStar/{roster_id}'
  data = {'star': position_id}
  r = session.post(url, data=data)
  return r.json()


@with_default_session
def append_to_ruleset(roster_data, target_ruleset_id,
    session=None):
  name = roster_data['name']
  _rejuvenate(roster_data)
  roster_id = create(target_ruleset_id, name, session=session)
  set_data(roster_data, roster_id, match_positions_by='none',
      session=session)
  return roster_id


@with_default_session
def clone_to_ruleset(roster_id, target_ruleset_id,
    session=None):
  roster_data = get_data(roster_id, flags=DETAILED_POSITIONS,
      session=session)
  return append_to_ruleset(roster_data, target_ruleset_id,
    session=session)


@exc.returns_api_error_checked_result
@with_default_session
def create(ruleset_id, name, session=None):
  """Creates a new roster and returns it's ID"""
  ruleset_id = str(ruleset_id)
  assert ruleset_id.isdecimal()
  data = {'ruleset': ruleset_id, 'name': name}
  url = session.baseurl / 'api/roster/create'
  r = session.post(url, data=data)
  return r.json()


@with_default_session
def get_data(roster_id, flags=0, session=None):
  """Returns a roster's data.

  Possible flags are:
  DETAILED_POSITIONS - provides a more detailed data for
      positions
  """
  roster_id = str(roster_id)
  assert roster_id.isdecimal()
  url = session.baseurl / f'api/roster/get/{roster_id}'
  r = session.get(url)
  roster_data = exc.api_error_checked(r.json())
  if roster_data == _NO_DATA:
    errfs = 'No roster exists with ID = {}.'
    raise NoRosterDataError(errfs.format(roster_id))
  if flags & DETAILED_POSITIONS:
    for position_data in roster_data.get('positions', []):
      if 'id' in position_data:
        position_id = position_data['id']
        detailed_position_data = position.get_data(position_id,
            session=session)
        position_data.update(detailed_position_data)
  if flags & DETAILED_STARS:
    for position_data in roster_data.get('stars', []):
      if 'id' in position_data:
        position_id = position_data['id']
        detailed_position_data = position.get_data(position_id,
            session=session)
        position_data.update(detailed_position_data)
  return roster_data


get = get_data


@exc.returns_api_error_checked_result
@with_default_session
def remove(ruleset_id, roster_id, session=None):
  ruleset_id = str(ruleset_id)
  assert ruleset_id.isdecimal()
  roster_id = str(roster_id)
  assert roster_id.isdecimal()
  url = session.baseurl / 'api/roster/remove'
  data = {'ruleset': ruleset_id, 'roster': roster_id}
  r = session.post(url, data=data)
  return r.json()


@exc.returns_api_error_checked_result
@with_default_session
def remove_star(roster_id, position_id, session=None):
  roster_id = str(roster_id)
  assert roster_id.isdecimal()
  position_id = str(position_id)
  assert position_id.isdecimal()
  url = session.baseurl / f'api/roster/removeStar/{roster_id}'
  data = {'star': position_id}
  r = session.post(url, data=data)
  return r.json()


@exc.returns_api_error_checked_result
@with_default_session
def search(name="___", owner=None, *, session=None):
  """Searches for rosters name and/or owner"""
  # https://fumbbl.com/index.php?name=PNphpBB2&file=viewtopic&p=681044&highlight=#681044
  s = str(name)
  if owner is not None:
    s = f'{owner}/{s}'
  data = {'search': s}
  url = session.baseurl / 'api/roster/search'
  r = session.post(url, data=data)
  return r.json()


@exc.returns_api_error_checked_result
@with_default_session
def search_by_owner(name, session=None):
  """Searches for rosters by a name string"""
  data = {'search': str(name)}
  url = session.baseurl / 'api/roster/search'
  r = session.post(url, data=data)
  return r.json()


@exc.returns_api_error_checked_result
@with_default_session
def _set_data(roster_id, keyvals, session=None):
  """Sets the preferences of a roster."""
  if isinstance(keyvals, dict):
    keyvals = [{'key': k, 'val': v} for k, v in keyvals.items()]
  roster_id = str(roster_id)
  assert roster_id.isdecimal()
  url = session.baseurl / f'api/roster/set/{roster_id}'
  data = {"data": json.dumps(keyvals)}
  r = session.post(url, data=data)
  return r.json()


@with_default_session
def set_data(roster_data, roster_id=None,
    match_positions_by='id',
    session=None):
  """Sets the preferences of a roster."""
  assert match_positions_by in ('none', 'id', 'title')
  working_keys = {
    'apothecary',
    'finesse',
    'info',
    'name',
    'necromancer',
    'physique',
    'playable',
    'raisePosition',
    'rerollCost',
    'undead',
    'versatility',
  }
  _roster_data = copy.deepcopy(roster_data)

  if roster_id is None:
    if 'id' in roster_data:
      roster_id = roster_data['id']
      del _roster_data['id']
    else:
      raise AttributeError('roster id is not defined')
  elif 'id' in roster_data:
    del _roster_data['id']

  if {'positions', 'stars'} & set(_roster_data):
    old_data = get_data(roster_id, session=session)

  if 'positions' in _roster_data:
    if match_positions_by != 'none':
      old_positions = {p[match_positions_by]: p
          for p in old_data['positions']
          if match_positions_by in p}
      new_positions = {p[match_positions_by]: p
          for p in _roster_data['positions']
          if match_positions_by in p}
      for k in set(old_positions) - set(new_positions):
        position.remove(roster_id, old_positions[k]['id'],
            session=session)
    for position_data in _roster_data['positions']:
      position_id = position_data.get('id')
      if match_positions_by != 'none':
        old_position_data = old_positions.get(position_data.get(
            match_positions_by))
        if old_position_data:
          position_id = old_position_data['id']
      if position_id is None:
        position_id = position.create(roster_id,
            position_data['name'], session=session)
      position_data['id'] = position_id
      position.set_data(position_data, session=session)
    del _roster_data['positions']

  if 'stars' in _roster_data:
    old_stars = set(s['id'] for s in old_data.get('stars', [])
        if s.get('id'))
    new_stars = set(s['id'] for s in _roster_data['stars']
        if s.get('id'))
    for position_id in old_stars - new_stars:
      remove_star(roster_id, position_id, session=session)
    for position_id in new_stars - old_stars:
      add_star(roster_id, position_id, session=session)
    del _roster_data['stars']

  if 'stats' in _roster_data:
    for k, v in _roster_data['stats'].items():
      _roster_data[k] = v
    del _roster_data['stats']

  for k in _roster_data.keys():
    if k not in working_keys:
      wfs = 'not in working keys: {}'
      warnings.warn(wfs.format(k), FutureWarning)
  return _set_data(roster_id, _roster_data, session=session)
