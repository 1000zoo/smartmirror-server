import requests

url = 'http://192.168.0.41:5000/upload'  # 서버 URL

with open('image.jpg', 'rb') as f:
    files = {'file': f}
    print(files)
    response = requests.post(url, files=files)

print(response.text)  # 서버에서 반환하는 응답 출력
