import functools
import inspect

import requests
import yarl


_session = None


def session():
  global _session
  if _session is None:
    _session = requests.Session()
    _session.baseurl = yarl.URL('https://fumbbl.com')
  return _session


def with_default_session(func):
  @functools.wraps(func)
  def decorated_func(*args, **kwargs):
    global _session
    argspec = inspect.getfullargspec(func)
    if argspec.kwonlydefaults:
      _args = args
      _kwargs = dict(argspec.kwonlydefaults)
    else:
      _args = []
      kwvals = list(argspec.defaults)
      ikw = len(argspec.args) - len(kwvals)
      for i, a in enumerate(args):
        if i < ikw:
          _args.append(a)
        if i in range(ikw, ikw + len(kwvals)):
          kwvals[i-ikw] = a
      _kwargs = dict(zip(
          argspec.args[-len(kwvals):],
          kwvals,
          ))
    _kwargs.update(kwargs)
    if _kwargs['session'] is None:
      _kwargs['session'] = session()
    return func(*_args, **_kwargs)
  return decorated_func
