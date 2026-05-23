import os
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = os.environ.get('BASE_URL', 'http://localhost:8000')

def post(path, data, headers=None):
    url = BASE + path
    body = json.dumps(data).encode('utf-8')
    hdrs = {'Content-Type': 'application/json'}
    if headers:
        hdrs.update(headers)
    req = Request(url, data=body, headers=hdrs, method='POST')
    try:
        with urlopen(req) as resp:
            return resp.read().decode('utf-8'), resp.getcode()
    except HTTPError as e:
        return e.read().decode('utf-8'), e.code

def get(path, headers=None):
    url = BASE + path
    hdrs = {}
    if headers:
        hdrs.update(headers)
    req = Request(url, headers=hdrs, method='GET')
    try:
        with urlopen(req) as resp:
            return resp.read().decode('utf-8'), resp.getcode()
    except HTTPError as e:
        return e.read().decode('utf-8'), e.code


def main():
    # Login
    login_data = {"email": "admin@local.com", "password": "Admin@123"}
    print('Logging in...')
    body, status = post('/auth/login', login_data)
    print('Login status:', status)
    print(body)
    try:
        j = json.loads(body)
        token = j.get('data', {}).get('access_token') or j.get('data', {}).get('token') or j.get('data', {}).get('accessToken')
    except Exception:
        token = None
    if not token:
        print('Failed to get token, aborting')
        return 1

    auth_header = {'Authorization': f'Bearer {token}'}

    # Create customer
    customer = {"nome": "Teste Cliente", "cpf": "12345678901", "telefone": "11999990000", "email": "cliente.teste@local", "endereco": "Rua Teste, 123"}
    print('\nCreating customer...')
    body, status = post('/customers', customer, headers=auth_header)
    print('Create status:', status)
    print(body)

    # List customers
    print('\nListing customers...')
    body, status = get('/customers', headers=auth_header)
    print('List status:', status)
    print(body)

    # Filter by cpf
    print('\nFiltering by cpf...')
    body, status = get(f'/customers?cpf={customer["cpf"]}', headers=auth_header)
    print('Filter status:', status)
    print(body)

    return 0

if __name__ == '__main__':
    raise SystemExit(main())
