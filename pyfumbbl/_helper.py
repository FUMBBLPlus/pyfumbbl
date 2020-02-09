class LegacyDataConverter:

  keytrans = {}
  intkeys = {}

  @classmethod
  def keyval1(cls, e, key):
    val = e.get(key)
    key = cls.keytrans.get(key, key)
    if val is not None and key in cls.intkeys:
      if val == '':
        val = None
      else:
        val = int(val)
    return key, val

  @classmethod
  def keyval2(cls, e):
    val = e.text
    key = cls.keytrans.get(e.tag, e.tag)
    if val is not None and key in cls.intkeys:
      if val == '':
        val = None
      else:
        val = int(val)
    return key, val

  @classmethod
  def update_with_keyvals1(cls, d, e):
    for key in e.keys():
      key, val = cls.keyval1(e, key)
      d[key] = val
