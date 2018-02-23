# coding=utf-8
from flask import Flask, render_template, send_from_directory, abort
from flask_httpauth import HTTPBasicAuth
import os
import logging

app = Flask(__name__)
app.config['CUSTOM_FILE_PATH'] = "D:\\system".decode('utf-8')
# app.config['CUSTOM_FILE_PATH'] = "\\".decode('utf-8')
app.config["IMG_EXT"] = ['.bmp', '.jpg', '.jpeg', '.png', '.gif']

auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'explorer':
        return '********'
    return None


@app.route("/")
@app.route('/list/')
@app.route('/list/<path:path_name>')
@auth.login_required
def main_list(path_name=None):
    if path_name is None:
        path_name = ''
    path = os.path.join(app.config["CUSTOM_FILE_PATH"], path_name)
    if not os.path.exists(path):
        abort(404)

    files = os.listdir(path)
    f = []
    for file in files:
        p = os.path.join(path, file)
        d = {'name': file, 'path': os.path.join(path_name, file).replace(os.path.sep, '/')}
        if os.path.isdir(p):
            d['type'] = 'folder'
        else:
            d['type'] = 'file'
        f.append(d)
    return render_template('index.html', files=f, path=path_name, name=os.path.split(path_name)[1],
                           up_dir=os.path.split(path_name)[0])


@app.route('/file/<path:file_path>')
def custom_file(file_path):
    return send_from_directory(app.config['CUSTOM_FILE_PATH'], file_path)


@app.route('/img/')
@app.route('/img/<path:file_path>')
@auth.login_required
def list_img(file_path=None):
    if file_path is None:
        file_path = ''
    path = os.path.join(app.config["CUSTOM_FILE_PATH"], file_path)
    files = os.listdir(path)
    f = []
    for file in files:
        p = os.path.join(path, file)
        d = {'name': file}
        if is_image(p):
            d['type'] = 'image'
            d['img_path'] = os.path.join(file_path, file).replace(os.path.sep, '/')
        elif os.path.isdir(p):
            sub_files = os.listdir(p)
            flag = False
            for sub_file in sub_files:
                if is_image(sub_file):
                    flag = True
                    break
            if flag:
                d['type'] = 'img_folder'
                d['path'] = os.path.join(file_path, file).replace(os.path.sep, '/')
                d['img_path'] = os.path.join(file_path, file, sub_file).replace(os.path.sep, '/')
            else:
                d['type'] = 'folder'
                d['path'] = os.path.join(file_path, file).replace(os.path.sep, '/')
        else:
            d['type'] = 'file'
            d['path'] = os.path.join(file_path, file).replace(os.path.sep, '/')
        f.append(d)
    return render_template('img.html', imges=f, name=os.path.split(file_path)[1], path=file_path,
                           up_dir=os.path.split(file_path)[0])


def is_image(name):
    ext = os.path.splitext(name)[1].lower()
    return ext in app.config['IMG_EXT']


if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=80, threaded=True)
