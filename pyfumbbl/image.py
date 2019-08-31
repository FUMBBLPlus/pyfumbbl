import mimetypes
import os
import pathlib

from pyfumbbl._session import with_default_session
from pyfumbbl import exc

__all__ = [
    'download',
    'get',
  ]

extension_fix = {
    '.jpe': '.jpg',
}


@with_default_session
def download_data(image_id, directory, session=None):
  """Downloads the image to the given directory."""
  mime_type, data = get_data(image_id, session=session)
  if data:
    extension = mimetypes.guess_extension(mime_type)
    extension = extension_fix.get(extension, extension)
    p = pathlib.Path(directory) / f'{image_id}{extension}'
    with open(p, 'wb') as f:
      f.write(data)
      return p


download = download_data


@with_default_session
def get_data(image_id, session=None):
  """Returns the mime type and the bytes of a hosted image."""
  image_id = str(image_id)
  assert image_id.isdecimal()
  urlfs = 'https://fumbbl.com/i/{}'
  r = session.get(urlfs.format(image_id))
  mime_type = r.headers.get('Content-Type')
  return mime_type, r.content


get = get_data
