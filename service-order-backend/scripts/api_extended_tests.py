import os, sys, json, subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = os.environ.get('BASE_URL', 'http://localhost:8000')


def run_cmd(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout.strip(), p.returncode


def request(method, path, token=None, data=None):
    url = BASE + path
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        body = None
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req) as resp:
            return resp.read().decode('utf-8'), resp.getcode()
    except HTTPError as e:
        return e.read().decode('utf-8'), e.code


def main():
    # get token
    token, rc = run_cmd([sys.executable, os.path.join(os.path.dirname(__file__), 'generate_admin_token.py')])
    if rc != 0 or not token:
        print('Failed to generate token')
        return 1
    print('Token:', token[:20] + '...')

    # list customers
    body, status = request('GET', '/customers', token=token)
    print('\nGET /customers', status)
    print(body)
    try:
        j = json.loads(body)
        customers = j.get('data', [])
        if not customers:
            print('No customers found')
            return 1
        customer = customers[0]
        cid = customer['id']
    except Exception as e:
        print('Failed to parse customers', e)
        return 1

    # update customer
    update = {'nome': 'Cliente Atualizado', 'telefone': '11911112222'}
    body, status = request('PUT', f'/customers/{cid}', token=token, data=update)
    print('\nPUT /customers/{cid}', status)
    print(body)

    # get customer
    body, status = request('GET', f'/customers/{cid}', token=token)
    print('\nGET /customers/{cid}', status)
    print(body)

    # create service order (try with and without trailing slash)
    so_body = {'title': 'Teste Ordem', 'description': 'Descrição teste'}
    body, status = request('POST', f'/service-orders?customer_id={cid}', token=token, data=so_body)
    if status == 307 or (not body) or ('id' not in (json.loads(body).get('data', {}) if body else {})):
        body, status = request('POST', f'/service-orders/?customer_id={cid}', token=token, data=so_body)
    print('\nPOST /service-orders?customer_id={cid}', status)
    print(body)
    try:
        j = json.loads(body)
        so_id = j.get('data', {}).get('id')
    except Exception:
        so_id = None
    if not so_id:
        print('Failed to create service order')
        return 1

    # get service order
    body, status = request('GET', f'/service-orders/{so_id}', token=token)
    print('\nGET /service-orders/{so_id}', status)
    print(body)

    # update service order
    body, status = request('PUT', f'/service-orders/{so_id}', token=token, data={'status': 'IN_PROGRESS'})
    print('\nPUT /service-orders/{so_id}', status)
    print(body)

    # delete service order
    body, status = request('DELETE', f'/service-orders/{so_id}', token=token)
    print('\nDELETE /service-orders/{so_id}', status)
    print(body)

    # delete customer
    body, status = request('DELETE', f'/customers/{cid}', token=token)
    print('\nDELETE /customers/{cid}', status)
    print(body)

    # confirm delete
    body, status = request('GET', f'/customers/{cid}', token=token)
    print('\nGET /customers/{cid} after delete', status)
    print(body)

    return 0

if __name__ == '__main__':
    raise SystemExit(main())
