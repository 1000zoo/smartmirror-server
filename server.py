from flask import Flask, request, jsonify
import os
import json
import http



"""
patinets-info =>
{
    "user": [
        {
            "barcode": "12345678",
            "name"   : "ooo",
            "gender" : "male",
            "birth"  : "yyyy-mm-dd"     ## gender와 birth는 없어져도 될듯
        },
        {...},{...}...,{...}    
    ]
}
"""

## HTTP Response Code
SUCCESS_CODE = '202'
UNKNOWN_ERROR_CODE = '404'
DUPLICATED_ERROR_CODE = '409'
GONE_ERROR_CODE = '410'

app = Flask(__name__)

IMAGE_PATH = os.path.join("image-data")  ## 이미지 저장 경로
JSON_FILENAME = "patients-info.json"    ## 환자 정보 저장 경로
PATIENTS = {"user":[]}                  ## 중복확인 및 삭제를 위한 임시변수


## 이미지 저장 경로 확인 (없을 시 생성)
def check_dir(dir=IMAGE_PATH, dirpath="./"):
    if not dir in os.listdir(dirpath):
        print(f"{dirpath}/{dir}경로 생성")
        os.mkdir(os.path.join(dirpath, dir))


## 환자 정보가 담긴 json 파일 확인 (없을 시 생성)
def check_json_data():
    if not JSON_FILENAME in os.listdir():
        temp = {"user":[]}
        with open(JSON_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(temp, f, indent='\t', ensure_ascii=False)


## PATIENTS 변수에 patients-info.json 데이터 불러오기
def load_patients():
    check_json_data()
    global PATIENTS
    with open(JSON_FILENAME, 'r') as f:
        PATIENTS = json.load(f)


## patients-info.json 업데이트
def update_patients():
    with open(JSON_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(PATIENTS, f, indent='\t', ensure_ascii=False)


## 응답 메세지로 변환
def json_response(success: bool, message=""):
    return jsonify({'success': success, 'message': message})


## 이미 저장된 바코드인지 확인하는 메소드
def contains(barcode):
    for p in PATIENTS['user']:
        if p['barcode'] == barcode:
            return True
        
    return False



## 받아온 이미지를 저장
@app.route('/image-upload', methods=['POST'])
def upload():
    check_dir()                                 ## 혹시 모를 기본 경로 (image-data/) 확인
    file = request.files['file']
    filename = file.filename                    ## 이미지 및 파일명 로드 (파일명: 이름-바코드_날짜-시간)
    name, filename = filename.split("_")
    save_path = os.path.join(IMAGE_PATH, name)  ## 저장 경로 생성  
    check_dir(name, IMAGE_PATH)                 ## 저장 경로 확인

    file.save(os.path.join(save_path, filename))## 파일 저장
    return json_response(
        True, SUCCESS_CODE
    )


## 환자 정보 추가
@app.route('/patients-info', methods=['POST'])
def add_patients_info():
    load_patients()                             ## 환자 정보 로드
    _data = request.data
    _data = json.loads(_data)
    bar_info = _data['barcode']


    ## 중복확인, 중복 시 저장을 하지 않고, 클라이언트에 실패 코드 및 메세지 전송
    if contains(bar_info):
        return json_response(
            False, DUPLICATED_ERROR_CODE
        )

    PATIENTS['user'].append(_data)
    update_patients()
    
    return json_response(
        True, SUCCESS_CODE
    )

## 환자 정보 전송
@app.route('/patients-info', methods=['GET'])
def send_patients_info():
    load_patients()
    return jsonify(PATIENTS)


## 환자 정보 수정 (삭제)
@app.route('/patients-info/<barcode>', methods=['DELETE'])
def delete_patients_info(barcode):
    load_patients()

    for patient in PATIENTS['user']:
        if patient['barcode'] == barcode:
            PATIENTS['user'].remove(patient)
            update_patients()
            return json_response(
                True, SUCCESS_CODE
            )

    return json_response(
        False, GONE_ERROR_CODE
    )

@app.route('/patients-info/iscontains/<barcode>', methods=['GET'])
def is_contains(barcode):
    load_patients()
    return json_response(True, SUCCESS_CODE) if contains(barcode) else json_response(False, GONE_ERROR_CODE)
    

if __name__ == '__main__':
    app.run(host="192.168.0.45", port=5000, debug=True)
