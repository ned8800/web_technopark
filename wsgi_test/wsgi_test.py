from urllib import parse 
import pprint

def parse_multipart_form_data(environ):
    post_data = environ['wsgi.input'].read().decode('utf-8')
    content_type = environ['CONTENT_TYPE']
    sep = content_type[content_type.index('boundary=') + len('baundary='):]
    post_data = post_data.replace('\r\n', '')
    post_data = post_data.split('--' + sep)
    post_data.pop(0)
    post_data.pop()
    return post_data

def app(environ, start_response):
    pprint.pprint(environ)
    get_data = parse.parse_qs(environ['QUERY_STRING'])
    post_data = ''
    
    if environ['REQUEST_METHOD'] == 'POST':
        if environ['CONTENT_TYPE'] == 'application/x-www-form-urlencoded':
            post_data = parse.parse_qs(environ['wsgi.input'].read().decode('utf-8'))
        if environ['CONTENT_TYPE'].startswith('multipart/form-data'):
            post_data = parse_multipart_form_data(environ)
    
    print('get  params : ', get_data)    
    print('post params : ', post_data)    
    
    data = b'\nHello world\n'
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])

# gunicorn wsgi_test:app 
# конфигурация подтягивается сама, если находимся в директории

# curl -X GET "http://127.0.0.1:8001/?id=3&name=tim&age=21"

# multipart/form-data
# curl -X POST -F 'name=tim' -F 'id=3' -F 'email=tim@mail.ru' "http://127.0.0.1:8001/"

# application/x-www-form-urlencoded
# curl -X POST -d 'name=tim' -d 'id=3' -d 'email=tim@mail.ru' "http://127.0.0.1:8001/"

