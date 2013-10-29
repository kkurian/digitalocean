DigitalOcean for Python3
========================

This is a general wrapper around the DigitalOcean API.


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


Features:

- lazily creates a single SSL connection used for all requests
- can be used as the expression in a 'with' statement
- automatically retries/reconnects


Credits:

This module was inspired by, and includes parts of, a Gist
by Brad Conte (https://gist.github.com/B-Con/6431500). Thank you!
