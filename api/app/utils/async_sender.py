import httpx

"""
https://www.python-httpx.org/async/
"""

async def async_send(
    method,
    server_url,
    server_port,
    path_url,
    params=None,
    data=None,
    json=None,
    files=None,
    content_type=None,
    access_token=None,
    timeout=10,
):
    """ GET, POST, PUT, PATCH """
    # use multipart/form-data when your form includes any <input type="file"> elements
    headers = {}
    if content_type is not None:
        # headers['content-type'] = content_type,
        headers.update({'content-type': content_type})

    if access_token is not None:
        # headers["Authorization"] = access_token
        headers.update({'Authorization': access_token})

    url = f"http://{server_url}:{server_port}{path_url}"
    
    async with httpx.AsyncClient() as s:
        if method.lower() == "get":
            # Get, no data=data
            r = await s.get(url=url, params=params, headers=headers, timeout=timeout)
        elif method.lower() == "post":
            r = await s.post(url=url, params=params, data=data, json=json, files=files, headers=headers, timeout=timeout)
        elif method.lower() == "put":
            r = await s.put(url=url, params=params, data=data, json=json, files=files, headers=headers, timeout=timeout)
        elif method.lower() == "patch":
            r = await s.patch(url=url, params=params, data=data, json=json, files=files, headers=headers, timeout=timeout)
        elif method.lower() == "delete":
            r = await s.delete(url=url, params=params, headers=headers, timeout=timeout)
        else:
            raise Exception('Not Implemented Error!')
    return r
