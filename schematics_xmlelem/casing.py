def _first_upper(v):
    if len(v) > 0:
        return v[0].upper() + v[1:]
    else:
        return v


def to_upper_camelcase(v):
    return ''.join(_first_upper(part) for part in v.split('_'))


def to_camelcase(v):
    parts = v.split('_')
    return parts[0] + ''.join(_first_upper(part) for part in parts[1:])

