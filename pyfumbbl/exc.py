import functools


__all__ = [
    'FUMBBLAPIError',
    'NoDataError',
    'NoSuccessError',
    'api_error_checked',
    'returns_api_error_checked_result',
  ]


API_ERROR_START = 'Error:'
API_ERROR_KEY = 'error'


class FUMBBLAPIError(Exception):
  pass


class NoDataError(Exception):
  pass


class NoSuccessError(Exception):
  pass


def api_error_checked(o):
  if isinstance(o, str) and o.startswith(API_ERROR_START):
    raise FUMBBLAPIError(o[len(API_ERROR_START):])
  elif (isinstance(o, dict) and len(o) == 1
      and API_ERROR_KEY in o):
    raise FUMBBLAPIError(o[API_ERROR_KEY])
  else:
    return o


def returns_api_error_checked_result(func):
  @functools.wraps(func)
  def decorated_func(*args, **kwargs):
    return api_error_checked(func(*args, **kwargs))
  return decorated_func
