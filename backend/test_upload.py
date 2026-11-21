import sys
import requests

def upload(image_path, url='http://localhost:5000/api/analyze'):
    with open(image_path, 'rb') as f:
        files = {'file': (image_path, f, 'image/jpeg')}
        try:
            resp = requests.post(url, files=files, timeout=60)
        except Exception as e:
            print('Request error:', e)
            return 1

    try:
        print('Status:', resp.status_code)
        print('Response JSON:')
        print(resp.json())
    except Exception:
        print('Non-JSON response:')
        print(resp.text)
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python test_upload.py path/to/image.jpg')
        sys.exit(1)
    image_path = sys.argv[1]
    sys.exit(upload(image_path))
