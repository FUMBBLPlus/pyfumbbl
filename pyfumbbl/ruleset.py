#import copy
import json
#import warnings

from pyfumbbl._session import with_default_session
from pyfumbbl import exc


__all__ = [
    'get',
    'set_options',
  ]


DEFAULT_SPP_LIMITS = "6,16,31,51,76,176"
DEFAULT_PREDETERMINED = "1:3N,4:2ND"


@exc.returns_api_error_checked_result
@with_default_session
def get_data(ruleset_id, session=None):
  """Returns a ruleset's data."""
  ruleset_id = str(ruleset_id)
  assert ruleset_id.isdecimal()
  url = session.baseurl / f'api/ruleset/get/{ruleset_id}'
  r = session.get(url)
  return r.json()


get = get_data


@exc.returns_api_error_checked_result
@with_default_session
def set_options(ruleset_id, keyvals, session=None):
  """Sets the options of a ruleset."""
  if isinstance(keyvals, dict):
    keyvals = [{'key': k, 'val': v} for k, v in keyvals.items()]
  ruleset_id = str(ruleset_id)
  assert ruleset_id.isdecimal()
  url = session.baseurl / f'api/ruleset/setoptions/{ruleset_id}'
  r = session.post(url, data={"options": json.dumps(keyvals)})
  return r.json()
