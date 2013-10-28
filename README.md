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

    > api.request('droplets', {'ids': [4242]})
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
    - Lazily creates a single SSL connection used for all requests.
    - Can be used as the expression in a 'with' statement.
    - Closes the SSL connection upon deletion of the instance or, when
      used as an expression in a 'with' statement, upon exiting the 'with'
      statement
