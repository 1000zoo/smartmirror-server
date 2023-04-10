from flask import Flask, request
import os

app = Flask(__name__)
home_path = os.path.join("image-data")

def check_dir(dir=home_path, dirpath="./"):
    if not dir in os.listdir(dirpath):
        print(f"{dirpath}/{dir}경로 생성")
        os.mkdir(os.path.join(dirpath, dir))


@app.route('/upload', methods=['POST'])
def upload():
    check_dir()
    file = request.files['file']
    filename = file.filename
    name, filename = filename.split("_")
    save_path = os.path.join(home_path, name)
    check_dir(name, home_path)

    file.save(os.path.join(save_path, filename))
    return '파일이 업로드 되었습니다.'


if __name__ == '__main__':
    app.run(host="192.168.0.10", port=5000)
