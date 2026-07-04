from flask import session
import os
import requests

API_BASE_URL = os.getenv('API_URL', 'http://localhost:8000')


def api(endpoint, method='GET', data=None, json=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}

    token = session.get('admin_access_token')
    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=data)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, data=data, json=json)
        elif method == 'PUT':
            resp = requests.put(url, headers=headers, json=json)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Método {method} no soportado")

        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {'error': str(e), 'status_code': getattr(e.response, 'status_code', None)}

