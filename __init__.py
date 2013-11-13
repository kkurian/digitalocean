import sys

if sys.version_info[0] == 2:
    from digitalocean import DigitalOceanAPI
else:
    from .digitalocean import DigitalOceanAPI
