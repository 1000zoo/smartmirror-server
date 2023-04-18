from flask import Flask, request, jsonify, Response
import os
import json
import http


## TODO 1. 아래의 형식에 맞게 API 수정 해야댐
## TODO 2. response message 어떻게 해야 직관적이고 효율적일지
##          => 어떤 곳에서는 TF 리턴하고, 어떤곳에서는 데이터 리턴하고
##          => Error code 는 statusCode로 flutter에서 확인 가능.
##          => 내가 원하는 결과에 맞게 statusCode를 수정 가능한지
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
UNKNOWN_ERROR_CODE = 404
DUPLICATED_ERROR_CODE = 409
NOT_EXIST_ERROR_CODE = 410

error_dict = {
    SUCCESS_CODE : "성공",
    UPLOAD_SUCCESS_CODE : "업로드가 완료되었습니다.",
    UNKNOWN_ERROR_CODE : "알 수 없는 에러입니다.",
    DUPLICATED_ERROR_CODE : "이미 등록된 환자입니다.",
    NOT_EXIST_ERROR_CODE : "없는 환자입니다.",
}

app = Flask(__name__)

IMAGE_PATH = os.path.join("image-data")  ## 이미지 저장 경로
JSON_FILENAME = "patients-info.json"    ## 환자 정보 저장 경로
PATIENTS = {}                 ## 중복확인 및 삭제를 위한 임시변수


## 이미지 저장 경로 확인 (없을 시 생성)
def check_dir(dir=IMAGE_PATH, dirpath="./"):
    if not dir in os.listdir(dirpath):
        print(f"{dirpath}/{dir}경로 생성")
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
        response = '{"msg":' + error_dict[code] + "}"
    else:
        response = '{"msg":' + str(data) + "}"
    return Response(response, status=code)
    # return jsonify({'success': success, 'message': message})


## 이미 저장된 바코드인지 확인하는 메소드
def contains(barcode):
    return barcode in PATIENTS.keys()


## 환자 이름 찾기
def get_patients_name(barcode):
    if contains(barcode):
        return PATIENTS[barcode]['name']
    return None


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
        return get_response(SUCCESS_CODE, data)
    
    except:
        return get_response(UNKNOWN_ERROR_CODE)


## 환자 정보 추가
@app.route('/patients-info/<barcode>', methods=['POST'])
def add_patients_info(barcode):
    try:
        load_patients()                             ## 환자 정보 로드
        _data = request.data
        _data = json.loads(_data) ## 여기서 values 만 받아오도록 해야댐 [barcode] ?


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
        name = PATIENTS.pop(barcode, False)

        if name:
            return get_response(SUCCESS_CODE, name)
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


if __name__ == '__main__':
    # app.run(host="192.168.0.45", port=5000, debug=True)
    app.run(host="192.168.0.10", port=5000, debug=True)
