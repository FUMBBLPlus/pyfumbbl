from pyfumbbl._session import with_default_session
from pyfumbbl import exc


__all__ = [
    'get_skill_list',
    'skill_by_id',
    'skill_by_name',
    'skill_list',
  ]


_skill_list = None
_skill_by_id = None
_skill_by_name = None


@exc.returns_api_error_checked_result
@with_default_session
def get_skill_list(*, session=None):
  """Returns the skills dictionary."""
  url = 'https://fumbbl.com/api/skill/list'
  r = session.get(url)
  return r.json()


@with_default_session
def skill_by_id(id_, *, session=None):
  if _skill_list is None:
    skill_list(session=session)
  return _skill_by_id[id_]


@with_default_session
def skill_by_name(name, *, session=None):
  if _skill_list is None:
    skill_list(session=session)
  return _skill_by_name[name]


@with_default_session
def skill_list(force_refresh=False, session=None):
  global _skill_list
  global _skill_by_id
  global _skill_by_name
  if _skill_list is None or force_refresh:
    _skill_list = get_skill_list(session=session)
    _skill_by_id ={}
    _skill_by_name = {}
    for d in _skill_list:
      _skill_by_id[d['id']] = d
      _skill_by_name[d['name']] = d
  return _skill_list



