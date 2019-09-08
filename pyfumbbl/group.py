import json
from xml.etree import ElementTree


from pyfumbbl import _helper
from pyfumbbl._session import with_default_session
from pyfumbbl import exc
from pyfumbbl import match


__all__ = [
    'get',
    'members',
    'tournaments',
  ]


MEMBERS = 0b1
TOURNAMENTS = 0b10


@with_default_session
def _get_legacy_data(group_id, query=None, session=None):
  group_id = str(group_id)
  assert group_id.isdecimal()
  url = session.baseurl / 'xml:group'
  url = url.with_query(id=group_id)
  if query is not None:
    url = url.update_query(**query)
  xmlstr = session.get(url).text
  et = ElementTree.fromstring(xmlstr)
  r = LegacyDataConverter.convert(et)
  return r


@with_default_session
def get_data(group_id, flags=0, session=None):
  """Returns a group data."""
  r = _get_legacy_data(group_id, session=session)
  if flags & MEMBERS:
    r['members'] = get_members_data(group_id, session=session)
  if flags & TOURNAMENTS:
    r['tournaments'] = get_tournaments(
        group_id,
        session=session,
    )
  return r


get = get_data


@with_default_session
def get_members_data(group_id, session=None):
  """Returns a the list of member teams of a group."""
  query = {'op': 'members'}
  d = _get_legacy_data(group_id, query, session=session)
  return d.get('members', [])


members = get_members_data


@exc.returns_api_error_checked_result
@with_default_session
def get_tournaments_data(groupId, session=None):
  """Returns a the list of tournaments of a group."""
  url = session.baseurl / f'api/group/tournaments/{groupId}'
  r = session.get(url)
  return r.json()


tournaments = get_tournaments_data


class LegacyDataConverter(_helper.LegacyDataConverter):

  @classmethod
  def convert(cls, et):
    r = {'id': et.get('id')}
    for e in et:
      if e.tag == 'matches':
        r.update(LegacyMatchesDataConverter.convert(e))
      elif e.tag == 'members':
        r.update(LegacyMembersDataConverter.convert(e))
      elif e.tag == 'tournaments':
        r.update(LegacyTournamentsDataConverter.convert(e))
      else:
        key, val = cls.keyval2(e)
        r[key] = val
    return r


class LegacyMatchesDataConverter(_helper.LegacyDataConverter):

  @classmethod
  def convert(cls, et):
    L = []
    r = {'matches': L}
    for e in et:
      if e.tag == 'match':
        d = {}
        cls.update_with_keyvals1(d, e)
        for e2 in e:
          if e2.tag in ('home', 'away'):
            key = f'team{("home", "away").index(e2.tag) + 1}'
            d[key] = LegacyTeamDataConverter.convert(e2)
          else:
            key, val = cls.keyval2(e2)
            d[key] = val
            if key == 'date':
              date, time = val.split()
              d[key] = date
              d['time'] = time
        L.append(d)
      else:
        key, val = cls.keyval2(e)
        r[key] = val
    return r


class LegacyMembersDataConverter(_helper.LegacyDataConverter):

  keytrans = {
      'race': 'rosterName',
      'win': 'wins',
      'tie': 'ties',
      'lose': 'losses',
  }

  @classmethod
  def convert(cls, et):
    L = []
    r = {'members': L}
    for e in et:
      d = {'id': e.get('id')}
      for e2 in e:
        key, val = cls.keyval2(e2)
        d[key] = val
        if key == 'coach' and e2.get('id'):
          d['coachId'] = e2.get('id')
      L.append(d)
    return r


class LegacyTeamDataConverter(_helper.LegacyDataConverter):

  keytrans = {
      'player': 'playerId',
      'TD': 'score',
  }

  @classmethod
  def convert(cls, et):
    r = {'id': et.get('id')}
    for e in et:
      if e.tag == 'cas':
        r['casualties'] = d = {}
        cls.update_with_keyvals1(d, e)
      elif e.tag == 'performances':
        r['statistics'] = L = []
        for e2 in e:
          d = {}
          cls.update_with_keyvals1(d, e2)
          L.append(d)
      else:
        key, val = cls.keyval2(e)
        r[key] = val
    return r


class LegacyTournamentsDataConverter(
    _helper.LegacyDataConverter
  ):

  @classmethod
  def convert(cls, et):
    L = []
    r = {'tournaments': L}
    for e in et:
      d = {'id': e.get('id')}
      for e2 in e:
        key, val = cls.keyval2(e2)
        d[key] = val
        if e2.tag == 'members':
          d.update(LegacyMembersDataConverter.convert(e2))
        elif e2.tag == 'winner':
          if e2.get('id'):
            d['winnerTeamId'] = e2.get('id')
          else:
            d['winnerTeamId'] = None
      L.append(d)
    return r
