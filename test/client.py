import requests
import json

addurl = 'http://192.168.0.10:5000/patients-info/123478'  # 서버 URL
geturl = 'http://192.168.0.10:5000/patients-info'

temp = {
        "name" : "천지우",
        "gender" : "남자",
        "birth" : "2000-10-10"
    }

## add_patients_info 테스트 코드
# url = 'http://192.168.0.10:5000/patients-info/6845674'
# response = requests.post(url, json.dumps(temp))
# print(response.text)

## send_patients_info 테스트 코드
# url = 'http://192.168.0.10:5000/patients-info'
# response = requests.get(url)
# response = json.loads(response.text)
# print(response)

## send_patients_name 테스트 코드
# url = 'http://192.168.0.10:5000/patients-info/123478'
# response = requests.get(url)
# print(response.text)

## delete_patients_info 테스트 코드
# url = 'http://192.168.0.10:5000/patients-info/123478'
# response = requests.delete(url)
# print(response.text)

## is_contains 테스트 코드
url = 'http://192.168.0.10:5000/patients-info/iscontains/6845674'
response = requests.get(url)
print(response.text)