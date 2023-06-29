from flask import Flask, request, jsonify, Response
from datetime import datetime
import os
import json
from threading import Lock


"""
patinets-info =>
{
		"98966568" : {
			"name": "989",
			"gender": "남자",
			"birth": "2000-01-01"
		},
		"00000000" : {
			"name": "0",
			"gender": "남자",
			"birth": "2000-01-01"
		},
		"12345678" : {
			"name": "12",
			"gender": "남자",
			"birth": "2000-01-01"
		}
}
"""


## HTTP Response Code
SUCCESS_CODE = 200
UPLOAD_SUCCESS_CODE = 201
LOAD_SUCCESS_CODE = 202
JSON_LOAD_SUCCESS_CODE = 203
UNKNOWN_ERROR_CODE = 404
DUPLICATED_ERROR_CODE = 409
NOT_EXIST_ERROR_CODE = 410

code_dict = {
    SUCCESS_CODE : "작업이 완료되었습니다.",
    UPLOAD_SUCCESS_CODE : "업로드가 완료되었습니다.",
    UNKNOWN_ERROR_CODE : "알 수 없는 에러입니다.",
    DUPLICATED_ERROR_CODE : "이미 등록된 환자입니다.",
    NOT_EXIST_ERROR_CODE : "등록되지 않은 바코드입니다.",
}

app = Flask(__name__)

IMAGE_PATH = os.path.join("image-data")  ## 이미지 저장 경로
JSON_FILENAME = "patients-info.json"    ## 환자 정보 저장 경로
PATIENTS = {}                 ## 중복확인 및 삭제를 위한 임시변수
RECENT_FILE = "recent.txt"

data_lock = Lock()


def get_datetime():
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def logger(msg):
    msg = str(msg)
    time = get_datetime()
    
    os.system('echo ' + time + "::: " + msg)


## 이미지 저장 경로 확인 (없을 시 생성)
def check_dir(dir=IMAGE_PATH, dirpath="./"):
    if not dir in os.listdir(dirpath):
        msg = f"{dirpath}/{dir}경로 생성"
        logger(msg)
        os.mkdir(os.path.join(dirpath, dir))


## 환자 정보가 담긴 json 파일 확인 (없을 시 생성)
def check_json_data():
    if not JSON_FILENAME in os.listdir():
        temp = {}
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
def get_response(code, data=None):
    if not data:
        response = '{"msg":' + f'"{code_dict[code]}"' + "}"
    else:
        ## 보내는 데이터가 JSON 형식이라면 데이터만 보내고
        ## 아니라면 "msg" 에 감싸서 보낸다.
        response = str(data) if code == JSON_LOAD_SUCCESS_CODE else '{"msg":' + f'"{str(data)}"' + "}"

    return Response(response, status=code)


## 이미 저장된 바코드인지 확인하는 메소드
def contains(barcode):
    return barcode in PATIENTS.keys()


## 환자 이름 찾기
def get_patients_name(barcode):
    if contains(barcode):
        return PATIENTS[barcode]['name']
    return None

## 현재 날짜 기록
def write_date(path):
    with open(os.path.join(path, RECENT_FILE), 'w') as f:
        f.write(str(datetime.now().date()))
        

## 받아온 이미지를 저장
@app.route('/upload-image', methods=['POST'])
def upload():
    try:
        check_dir()                                 ## 혹시 모를 기본 경로 (image-data/) 확인
        file = request.files['file']
        filename = file.filename                    ## 이미지 및 파일명 로드 (파일명: 이름-바코드_날짜-시간)
        name, filename = filename.split("_")
        save_path = os.path.join(IMAGE_PATH, name)  ## 저장 경로 생성  
        check_dir(name, IMAGE_PATH)                 ## 저장 경로 확인
        write_date(save_path)
        file.save(os.path.join(save_path, filename))## 파일 저장
        return get_response(UPLOAD_SUCCESS_CODE)
    except:
        return get_response(UNKNOWN_ERROR_CODE)


## 환자 정보 전송
@app.route('/patients-info', methods=['GET'])
def send_patients_info():
    try:
        load_patients()
        data = json.dumps(PATIENTS)
        return get_response(JSON_LOAD_SUCCESS_CODE, data)
    
    except:
        return get_response(UNKNOWN_ERROR_CODE)


## 환자 정보 추가
@app.route('/patients-info/<barcode>', methods=['POST'])
def add_patients_info(barcode):
    try:
        load_patients()                             ## 환자 정보 로드
        _data = request.data
        _data = json.loads(_data) ## 여기서 values 만 받아오도록 해야댐 [barcode]


        ## 중복확인, 중복 시 저장을 하지 않고, 클라이언트에 실패 코드 및 메세지 전송
        if contains(barcode):
            return get_response(DUPLICATED_ERROR_CODE)

        PATIENTS[barcode] = _data
        update_patients()
        
        return get_response(SUCCESS_CODE)
    
    except:
        return get_response(UNKNOWN_ERROR_CODE)


## 환자 이름 전송
@app.route('/patients-info/<barcode>', methods=['GET'])
def send_patients_name(barcode):
    try:
        load_patients()
        name = PATIENTS.pop(barcode, False)["name"]
        if name:
            return get_response(LOAD_SUCCESS_CODE, name)
        else:
            return get_response(NOT_EXIST_ERROR_CODE)
        
    except:
        return get_response(UNKNOWN_ERROR_CODE)


## 환자 정보 수정 (삭제)
@app.route('/patients-info/<barcode>', methods=['DELETE'])
def delete_patients_info(barcode):
    try:
        load_patients()
        result = PATIENTS.pop(barcode, False)
        update_patients()

        if result:
            return get_response(SUCCESS_CODE)
        else:
            return get_response(NOT_EXIST_ERROR_CODE)
        
    except:
        return get_response(UNKNOWN_ERROR_CODE)


## 환자 찾기 (등록 유무 확인)
@app.route('/patients-info/iscontains/<barcode>', methods=['GET'])
def is_contains(barcode):
    try:
        load_patients()
        return get_response(SUCCESS_CODE) if contains(barcode) else get_response(NOT_EXIST_ERROR_CODE)
    
    except:
        return get_response(UNKNOWN_ERROR_CODE)
    

## 오늘 사진을 찍었는지 확인
@app.route('/shot-today/<barcode>', methods=['GET'])
def shot_today(barcode) -> Response:
    try:
        load_patients()
        patient = PATIENTS[barcode]['name']
        folder = f"{patient}-{barcode}"
        path = os.path.join(IMAGE_PATH, folder)
        file = os.path.join(path, RECENT_FILE)

        try:
            with open(file, 'r') as f:
                recent_date = f.read()
                today = recent_date == str(datetime.now().date())
                return get_response(SUCCESS_CODE, True) if today else get_response(SUCCESS_CODE, False)

        except:
            return get_response(SUCCESS_CODE, False)

    except:
        return get_response(UNKNOWN_ERROR_CODE)


if __name__ == '__main__': 
    app.run(host="192.168.0.45", port=8080, debug=True)
    # app.run(host="192.168.0.10", port=5000, debug=True)


