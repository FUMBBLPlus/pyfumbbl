import copy
import json
import warnings

from pyfumbbl._session import with_default_session
from pyfumbbl import exc
from pyfumbbl import image
from pyfumbbl import skill


__all__ = [
    'add_skill',
    'append_to_roster',
    'clone_to_roster',
    'create',
    'get',
    'get_skills',
    'remove',
    'remove_skill',
    'set_data',
  ]


def _rejuvenate(position_data, del_roster=True):
  if 'id' in position_data:
    del position_data['id']
  if 'roster' in position_data and del_roster:
    del position_data['roster']
  return position_data


@exc.returns_api_error_checked_result
@with_default_session
def add_skill(position_id, skill_id_or_name, *, session=None):
  skill_id_or_name = str(skill_id_or_name)
  if not skill_id_or_name.isdecimal():
    skill_data = skill.skill_by_name(
        skill_id_or_name,
        session=session
    )
    skill_id = skill_data['id']
  else:
    skill_id = int(skill_id_or_name)
  url = session.baseurl / f'api/position/addskill/{position_id}'
  data = {'skill': skill_id}
  r = session.post(url, data=data)
  return r.json()


@with_default_session
def append_to_roster(position_data, target_roster_id,
    *, session=None):
  position_data = copy.deepcopy(position_data)
  name = position_data.get('name') or position_data.get('title')
  _rejuvenate(position_data)
  position_id = create(target_roster_id, name, session=session)
  set_data(position_data, position_id, session=session)
  return position_id


@with_default_session
def clone_to_roster(position_id, target_roster_id,
    *, session=None):
  position_data = get_data(position_id, session=session)
  return append_to_roster(position_data, target_roster_id,
    session=session)


@with_default_session
def create(roster_id, name, *, session=None):
  """Creates a new position and returns it's ID"""
  roster_id = str(roster_id)
  assert roster_id.isdecimal()
  url = session.baseurl / f'api/position/create/{roster_id}'
  data = {'name': name}
  r = session.post(url, data=data)
  return r.json()


@exc.returns_api_error_checked_result
@with_default_session
def get_data(position_id, *, session=None):
  """Returns a positions's data."""
  position_id = str(position_id)
  assert position_id.isdecimal()
  url = session.baseurl / f'api/position/get/{position_id}'
  r = session.get(url)
  return r.json()


get = get_data


@exc.returns_api_error_checked_result
@with_default_session
def get_skills_data(position_id, *, session=None):
  """Return the skills of a position."""
  position_id = str(position_id)
  assert position_id.isdecimal()
  url = session.baseurl / f'api/position/skills/{position_id}'
  r = session.get(url)
  return r.json()


get_skills = get_skills_data


@exc.returns_api_error_checked_result
@with_default_session
def remove(roster_id, position_id, *, session=None):
  roster_id = str(roster_id)
  assert roster_id.isdecimal()
  position_id = str(position_id)
  assert position_id.isdecimal()
  url = session.baseurl / f'api/position/remove/{roster_id}'
  data = {'position': position_id}
  r = session.post(url, data=data)
  return r.json()


@exc.returns_api_error_checked_result
@with_default_session
def remove_skill(position_id, skill_id_or_name,
    *, session=None):
  skill_id_or_name = str(skill_id_or_name)
  if not skill_id_or_name.isdecimal():
    skill_data = skill.skill_by_name(
        skill_id_or_name,
        session=session
    )
    skill_id = skill_data['id']
  else:
    skill_id = int(skill_id_or_name)
  url = session.baseurl
  url /= f'api/position/removeSkill/{position_id}'
  data = {'skill': skill_id}
  r = session.post(url, data=data)
  return r.json()


@exc.returns_api_error_checked_result
@with_default_session
def _set_data(position_id, keyvals, *, session=None):
  """Sets the preferences of a position."""
  if isinstance(keyvals, dict):
    keyvals = [{'key': k, 'val': v} for k, v in keyvals.items()]
  position_id = str(position_id)
  assert position_id.isdecimal()
  url = session.baseurl / f'api/position/set/{position_id}'
  data = {"data": json.dumps(keyvals)}
  r = session.post(url, data=data)
  return r.json()


@with_default_session
def set_data(position_data, position_id=None, *, session=None):
  """Sets the preferences of a position."""
  working_keys = {
    'cost',
    'gender',
    'iconLetter',
    'name',
    'quantity',
    'race',
    'secretweapon',
    'skill.A',
    'skill.G',
    'skill.M',
    'skill.P',
    'skill.S',
    'stats.AG',
    'stats.AV',
    'stats.MA',
    'stats.ST',
    'thrall',
    'type',
    'undead',
  }
  _position_data = copy.deepcopy(position_data)
  if position_id is None:
    if 'id' in position_data:
      position_id = position_data['id']
      del _position_data['id']
    else:
      raise AttributeError('position id is not defined')
  elif 'id' in position_data:
    del _position_data['id']

  if {'skills'} & set(_position_data):
    old_data = get_data(position_id, session=session)

  for nd in ('normal', 'double'):
    k = '{}Skills'.format(nd)
    if k in _position_data:
      for category in _position_data[k]:
        _position_data['skill.{}'.format(category)] = nd
      del _position_data[k]

  if 'stats' in _position_data:
    for k, v in _position_data['stats'].items():
      _position_data['stats.{}'.format(k)] = v
    del _position_data['stats']

  if 'skills' in _position_data:
    old_skills = set(old_data.get('skills', []))
    new_skills = set(_position_data['skills'])
    for name in old_skills - new_skills:
      remove_skill(position_id, name=name, session=session)
    for name in new_skills - old_skills:
      add_skill(position_id, name=name, session=session)
    del _position_data['skills']

  for k in _position_data.keys():
    if k not in working_keys:
      wfs = 'set() may not support key: {}'
      warnings.warn(wfs.format(k), FutureWarning)
  return _set_data(position_id, _position_data, session=session)

