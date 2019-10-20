import copy
import json
from xml.etree import ElementTree

from pyfumbbl import _helper
from pyfumbbl._session import with_default_session
from pyfumbbl import exc

__all__ = [
    'get_all_matches',
    'get',
    'get_legacy_data',
    'get_matches',
    'get_options',
    'set_options_data',
  ]

WITH_LEGACY = 0b1
TEAM_OPTIONS = 0b10
PAST_PLAYERS = 0b100


@exc.returns_api_error_checked_result
@with_default_session
def get_all_matches(team_id, session=None):
  """Returns a list of match data with."""
  latest_match_id = None
  r = []
  n = 25
  while n == 25:
    batch = get_matches(
        team_id,
        latest_match_id=latest_match_id,
        session=session,
    )
    n = len(batch)
    if not n:
      break
    if latest_match_id is None:
      r.extend(batch)
    else:
      r.extend(batch[1:])
    latest_match_id = batch[-1]["id"]
  return r


@exc.returns_api_error_checked_result
@with_default_session
def get_data(team_id, flags=0, session=None):
  """Returns a teams data."""
  team_id = str(team_id)
  assert team_id.isdecimal()
  url = session.baseurl / f'api/team/get/{team_id}'
  r = session.get(url).json()
  if flags & TEAM_OPTIONS:
    r['options'] = get_options_data(team_id, session=session)
  if flags & WITH_LEGACY:
    rleg = get_legacy_data(team_id, flags, session=session)
    r.update(rleg)
  return r


get = get_data


@with_default_session
def get_legacy_data(team_id, flags=0, session=None):
  """Returns a teams data provided by the legacy API."""
  team_id = str(team_id)
  assert team_id.isdecimal()
  url = session.baseurl / 'xml:team'
  url = url.with_query(id=team_id)
  if flags & PAST_PLAYERS:
    url = url.update_query(past=1)
  xmlstr = session.get(url).text
  et = ElementTree.fromstring(xmlstr)
  r = LegacyDataConverter.convert(et)
  return r


@exc.returns_api_error_checked_result
@with_default_session
def get_matches(team_id, latest_match_id=None, session=None):
  """Returns a list of match data with a maximum length of 25."""
  team_id = str(team_id)
  assert team_id.isdecimal()
  if latest_match_id is None:
    url = session.baseurl / f'api/team/matches/{team_id}'
  else:
    latest_match_id = str(latest_match_id)
    assert latest_match_id.isdecimal()
    url = session.baseurl / f'api/team/matches/{team_id}/{latest_match_id}'
  r = session.get(url).json()
  return r


@exc.returns_api_error_checked_result
@with_default_session
def get_options_data(team_id, session=None):
  """Returns the data of team options."""
  team_id = str(team_id)
  assert team_id.isdecimal()
  url = session.baseurl / f'api/team/getOptions/{team_id}'
  r = session.get(url).json()
  # the following row is required to dodge this bug #203:
  # (https://fumbbl.com/p/bugs?id/203)
  r['tournamentSkills'] = json.loads(r['tournamentSkills'])
  return r


get_options = get_options_data


@exc.returns_api_error_checked_result
@with_default_session
def set_options_data(team_id, options_data, session=None):
  """Returns the data of team options."""
  team_id = str(team_id)
  assert team_id.isdecimal()
  url = session.baseurl / f'api/team/setOptions/{team_id}'
  d = options_data = copy.deepcopy(options_data)
  # the following row is required to dodge this bug #203:
  # (https://fumbbl.com/p/bugs?id/203)
  d['tournamentSkills'] = json.dumps(d['tournamentSkills'])
  r = session.post(url, data={"options": json.dumps(d)})
  return r.json()


class LegacyDataConverter(_helper.LegacyDataConverter):

  keytrans = {
      'currentSpps': 'spp',
      'nr': 'number',
      'playerStatistics': 'statistics',
  }

  @classmethod
  def convert(cls, et):
    r = {'players': []}
    cls.update_with_keyvals1(r, et)
    for e in et:
      if e.tag == 'lastMatch':
        r['lastMatch'] = {'id': e.text}
        cls.update_with_keyvals1(r['lastMatch'], e)
      elif e.tag == 'record':
        for e2 in e:
          key, val = cls.keyval2(e2)
          r[key] = val
      elif e.tag == 'player':
        p = {'skills': [], 'injuries': []}
        cls.update_with_keyvals1(p, e)
        if p['status'] == 'Active':
          r['players'].append(p)
        else:
          r.setdefault('pastplayers', []).append(p)
        for e2 in e:
          if e2.tag == 'skillList':
            p['skills'].extend(e3.text for e3 in e2)
          elif e2.tag == 'injuryList':
            p['injuries'].extend(e3.text for e3 in e2)
          elif e2.tag == 'playerStatistics':
            cls.update_with_keyvals1(p, e2)
            for e3 in e2:
              key, val = cls.keyval2(e3)
              p[key] = val
          else:
            key, val = cls.keyval2(e2)
            p[key] = val
      else:
        key, val = cls.keyval2(e)
        r[key] = val
    return r
