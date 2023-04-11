from flask import Flask, request
import os
import json

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
app = Flask(__name__)
home_path = os.path.join("image-data")
json_filename = "patients-info.json"
patients = {"user":[]}


def check_dir(dir=home_path, dirpath="./"):
    if not dir in os.listdir(dirpath):
        print(f"{dirpath}/{dir}경로 생성")
        os.mkdir(os.path.join(dirpath, dir))

def check_json_data():
    if not json_filename in os.listdir():
        temp = {"user":[]}
        with open(json_filename, 'w') as f:
            json.dump(temp, f)


@app.route('/image-upload', methods=['POST'])
def upload():
    check_dir()
    file = request.files['file']
    filename = file.filename
    name, filename = filename.split("_")
    save_path = os.path.join(home_path, name)
    check_dir(name, home_path)

    file.save(os.path.join(save_path, filename))
    return '파일이 업로드 되었습니다.'


@app.route('/patients-info', methods=['POST'])
def add_patients_info():
    _data = request.data
    _data = json.loads(_data)
    bar_info = _data['barcode']

    patients['user'].append(_data)
    print(patients)
    return '정보추가'


@app.route('/patients-info', methods=['GET'])
def load_patients_info():
    pass


@app.route('/patients-info', methods=['POST'])
def mod_patients_info():
    print('mod')
    return "mod"


def update_patients():
    check_json_data()
    global patients
    with open(json_filename, 'r') as f:
        patients = json.load(f)
    

if __name__ == '__main__':
    update_patients()
    app.run(host="192.168.0.45", port=5000, debug=True)
