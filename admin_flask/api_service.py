import requests
from flask import session
import os

API_BASE_URL = os.getenv('API_URL', 'http://localhost:8000')

def api_request(endpoint, method='GET', data=None, json=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    token = session.get('admin_access_token')
    
    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=data)
        elif method == 'POST':
            # Soporte automático tanto para form-data como para JSON estructurado
            if endpoint == '/auth/login' or data:
                resp = requests.post(url, headers=headers, data=data, json=json)
            else:
                resp = requests.post(url, headers=headers, json=json)
        elif method == 'PUT':
            resp = requests.put(url, headers=headers, json=json)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Método {method} no soportado")

        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        # Intenta recuperar el mensaje detallado de error enviado por FastAPI
        try:
            err_json = e.response.json()
            if 'detail' in err_json:
                return {'error': err_json['detail'], 'status_code': getattr(e.response, 'status_code', None)}
        except:
            pass
        return {'error': str(e), 'status_code': getattr(e.response, 'status_code', None)}

# Alias global para máxima compatibilidad con los blueprints importados
api = api_request