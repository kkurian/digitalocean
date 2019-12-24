**Note: not maintained**

DigitalOcean for Python 2 and 3
===============================

This is a general wrapper around the DigitalOcean API. It works at least in
Python 2.7 and 3.3.


Example Usage:

    > api = DigitalOceanAPI(
        MY_CLIENT_ID,
        MY_API_KEY,
        pemfile='/etc/ssl/certs/ca-certificates.pem')

    > api.request('droplets')
    < {'status': 'OK', 'droplets': [{...}, ...]}

    > api.request('droplets', ids=[4242])
    < {'status': 'OK', 'droplet': {...}}

    > api.request('images')
    < {'status': 'OK', 'images': [{'distribution': 'CentOS', ...}, ...]}

    > api.request('droplets/new', {
        'name': 'example',
        'size_id': 66,
        'image_id': 473123,
        'region_id': 4})
    < {'status': 'OK', 'droplet': {'size_id': 66, ...}}


Credits:

This module was originally inspired by a Gist by Brad Conte
(https://gist.github.com/B-Con/6431500).
