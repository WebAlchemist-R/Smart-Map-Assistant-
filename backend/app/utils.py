def safe_get(d, k, default=None):
    return d.get(k, default) if isinstance(d, dict) else default
