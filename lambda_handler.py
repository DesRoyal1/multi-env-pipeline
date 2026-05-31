import json
import io
import sys
from app import app

def handler(event, context):
    path = event.get('rawPath', '/')
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    headers = event.get('headers', {}) or {}
    body = event.get('body', '') or ''
    query = event.get('rawQueryString', '')

    if query:
        path = f"{path}?{query}"

    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'wsgi.input': io.BytesIO(body.encode() if isinstance(body, str) else body),
        'wsgi.errors': sys.stderr,
        'wsgi.url_scheme': 'https',
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'SERVER_NAME': 'lambda',
        'SERVER_PORT': '443',
    }

    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value

    response_started = []
    response_body = []

    def start_response(status, response_headers, exc_info=None):
        response_started.append((status, response_headers))

    result = app(environ, start_response)
    for chunk in result:
        response_body.append(chunk)

    status_code = int(response_started[0][0].split(' ')[0])
    response_headers = dict(response_started[0][1])

    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': b''.join(response_body).decode('utf-8')
    }
