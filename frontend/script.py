import requests

if __name__ == '__main__':
    resp = requests.get('http://0.0.0.0:8080/')
    print(resp.text)