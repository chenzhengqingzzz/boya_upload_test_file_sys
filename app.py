# -*- coding: utf-8 -*-
import sys
import json
import shutil
import datetime
import subprocess
import threading
import os
from pathlib import Path
import psutil
import traceback

from flask import Flask, render_template, request, send_file, jsonify, session, has_request_context
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from unittest.mock import patch
from threading import Lock, Thread
from io import StringIO
from functools import wraps
from multiprocessing import Process
# import logging
# logging.basicConfig(level=logging.DEBUG)  # 设置日志级别为DEBUG
# from werkzeug.utils import secure_filename
# from pyLib import *

status_file_path = Path("update_status.json")

class FakeTk:
    def __init__(self, *args, **kwargs):
        pass

    def withdraw(self):
        pass

    def mainloop(self):
        pass

    def destroy(self):
        pass

module = None
lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "BYKJ88*"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

sids = {}
console_output = {}

# 保存原始的 sys.stdout
original_stdout_write = sys.stdout.write
original_stderr_write = sys.stderr.write

def wrapper_write(text):
    sid = (request.sid if hasattr(request, 'sid') else sids.get(request.args.get('sid', None), None)) if has_request_context() else None
    if sid and text.strip():
        console_output[sid].append(str(text))
        real_ip = request.headers.get('X-Real-IP', request.remote_addr)
        message = f"{real_ip}: {text}"
        socketio.emit("console_log", message, room=sid)
    original_stdout_write(text)
    sys.stdout.flush()

@socketio.on("connect")
def ws_connect(auth):
    sid = request.sid
    sids[sid] = sid
    if sid not in console_output:
        console_output[sid] = []
    print(f"Socket.IO connected to: {request.sid}")

@socketio.on("disconnect")
def ws_disconnect():
    sid = request.sid
    print(f"Socket.IO disconnected from: {sid}")
    sids.pop(sid, None)
    console_output.pop(sid, None)

@app.before_request
def before_request():
    print(f"{request.method} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {request.url}")

# ======================== Helper Functions ========================

def import_and_run(module_path, file_path):
    sys.stdout.write = wrapper_write
    with open(module_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 为模块创建一个命名空间，并设置 '__name__' 为 '__main__'
    module_namespace = {'__name__': '__main__'}
    with patch('tkinter.filedialog.askdirectory', return_value=str(file_path)):
        with patch('tkinter.filedialog.askopenfilename', return_value=str(file_path)):
            with patch('tkinter.Tk', FakeTk):
                try:
                    exec(code, module_namespace)
                except Exception as e:
                    print(f"Error: {e}")
                    module_name = None
                    if "No module named" in str(e):
                        module_name = str(e).split("'")[1]
                    # 尝试安装缺少的模块
                    if module_name:
                        result = subprocess.run([sys.executable, "-m", "pip", "install", module_name])
                        if result.returncode == 0:
                            print(f"Successfully installed {module_name}.")
                            # 重新运行脚本
                            exec(code, module_namespace)
                        else:
                            print(f"Failed to install {module_name}.")
                    else:
                        # 处理其他异常
                        traceback.print_exc()
                        print("An error occurred. Unable to install missing modules.")

def perl_run(module_path, command, use_shell, file_path):
    with open(module_path, 'r', encoding='utf-8') as f:
        code = f.read()

    with open(Path(file_path) / Path(module_path).name, 'w', encoding='utf-8') as temp_file:
        temp_file.write('$| = 1;\n')
        temp_file.write(code)

    result = subprocess.Popen([command, Path(file_path) / Path(module_path).name], cwd=file_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=use_shell)
    print(f"脚本输出：")
    for line in result.stdout:
        print(line.strip())
    (Path(file_path) / Path(module_path).name).unlink()

def get_filePath_list(file_path, extension, filelist=[]):
    if file_path.is_dir():
        for item in Path(file_path).glob("*"):
            get_filePath_list(item, extension, filelist)
    elif file_path.suffix == extension:
        if file_path not in filelist:
            filelist.append(file_path)
    return filelist

def get_last_modified_times(directory):
    """
    获取目录中所有文件的上次修改时间戳并存储在字典中
    """
    last_modified_times = {}
    for item in Path(directory).iterdir():
        if item.is_file():
            last_modified_times[str(item)] = item.stat().st_mtime
        elif item.is_dir():
            last_modified_times.update(get_last_modified_times(str(item)))  # 注意这里的更新操作
    return last_modified_times


def check_for_changes(directory, last_modified_times):
    """
    检查目录中的文件变化（新增、修改和删除）并返回相应的文件列表
    """
    new_files = []
    modified_files = []
    deleted_files = []
    

    filelist = list(get_last_modified_times(directory).keys())

    for item in filelist:
        item = Path(item)  # 将item转换成Path对象
        if str(item) not in last_modified_times:
            # 文件是新增的
            new_files.append(str(item))
        else:
            # 检查文件是否被修改（基于修改时间戳）
            current_mtime = item.stat().st_mtime
            if current_mtime != last_modified_times[str(item)]:
                # 文件已被修改
                modified_files.append(str(item))
                # 从字典中移除文件以跟踪删除的文件
                del last_modified_times[str(item)]
    # last_modified_times 字典中剩余的项目代表已删除的文件
    deleted_files = [str(item) for item in last_modified_times.keys()]

    # # 过滤新生成的文件，只保留名字中包含"log"、后缀为".xlsx"的文件
    # new_files = [f for f in new_files if "log" in f or f.endswith(".xlsx")]

    return new_files, modified_files, deleted_files

def rmFileAndDir(temp_folder):
    """Clear the temp folder."""
    folder_path = Path(temp_folder)
    for item in folder_path.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
            elif item.is_file():
                item.unlink()
        except Exception as e:
            print(e)

def deleteOldestFolder(temp_folder):
    try:
        folder_path = Path(temp_folder)

        folder_list = [f for f in folder_path.iterdir() if f.is_dir()]
        for path in folder_list:
            folders = [f for f in path.iterdir() if f.is_dir()]
            
            if len(folders) <= 15:
                continue
            while len(folders) > 15:
                oldest_folder = min(folders, key=lambda f: f.stat().st_ctime)
                shutil.rmtree(oldest_folder)
                folders = [f for f in path.iterdir() if f.is_dir()]
            print("================== %s 已保留生成最新的15个日志文件夹（定期清理） =================="%str(path.name))
    except Exception as e:
        print(e)


def get_filePath_fileName_fileExt(filename):
    """Extract file path, file name, and file extension from a given filename."""
    path = Path(filename)
    return path.parent, path.stem, path.suffix

# 获取路径的函数
def get_directory_structure(rootdir):
    """
    Create a nested dictionary from the rootdir, sorted by the timestamp in filenames/directory names.
    """
    directory = {}
    rootdir = Path(rootdir)

    # Sort items based on their names (which contain timestamps) in ascending order
    items = sorted(rootdir.iterdir(), key=lambda x: x.name)

    for item in items:
        if item.is_dir():
            directory[item.name] = get_directory_structure(item)
        else:
            directory[item.name] = item
    return directory

# 获取脚本库
def get_py_scripts_from_pyLib():
    path_to_pyLib = Path('./pyLib')
    py_files = [f.name for f in path_to_pyLib.glob('*.p[y|l]') if f.is_file() and f.name != "__init__.py"]
    return py_files


# ======================== Flask Routes ========================

@app.route('/')
def index():
    folder_path = Path(f"temp/{request.headers.get('X-Real-IP', request.remote_addr)}")
    directory_structure = get_directory_structure(folder_path) if folder_path.exists() else {}

    py_scripts = get_py_scripts_from_pyLib()

    uploaded_files = session.get('uploaded_files')
    no_files = request.args.get('no_files', default=False, type=bool)
    # log_files = request.args.get('log_files', default='')
    log_files = session.get('OutFileList', [])

    # 从session中获取之前选择的脚本名
    selected_script_for_choose = session.get('selected_script_for_choose', 'default')  # default为默认值
    selected_script_for_path = session.get('selected_script_for_path', 'default')  # default为默认值

    if not isinstance(log_files, list):
        log_files = [log_files]
    rendered_template = render_template('index.html', log_entries='', log_files=log_files, uploaded_files=uploaded_files, no_files=no_files, files_structure=directory_structure, py_scripts=py_scripts, selected_script_for_choose=selected_script_for_choose, selected_script_for_path=selected_script_for_path,)
    if 'OutFileList' in session:
        del session['OutFileList']
    if 'uploaded_files' in session:
        del session['uploaded_files']
    return rendered_template

@app.route('/get_socketid', methods=['POST'])
def get_socket_id():
    try:
        data = request.get_json()
        sid = data.get('sid')
        session['sid'] = sid
        if sid not in console_output:
            console_output[sid] = []
        print(f"Success! Received socket.id: {session['sid']}")
        return jsonify({'message': f"Success! Received socket.id: {session['sid']}"})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download_log/<path:filename>')  # 使用 path 而不是 string 可以接受斜杠
def download_log(filename):
    if sys.platform.startswith('linux') and filename[:2] == "Z/":
        filename = f"/{filename}"

    file_path = Path(filename)
    full_path = file_path.resolve()  # 获取文件的绝对路径

    print(f"尝试寻找目标路径的文件: {full_path}")  # 打印调试信息

    if full_path.exists():
        print("文件已获取，正在尝试下载...")
        return send_file(full_path, as_attachment=True)
    else:
        print("目标路径的文件未找到！！！")
        return "目标路径的文件未找到！！！", 404  # 返回 404 状态码和错误信息

def updateFiles():
    if sys.platform.startswith('linux'):
        update_path = Path(r'/Z/misc/testing/ATE/K2/zqchen/Program/boya_upload_test_file_sys')
    elif sys.platform.startswith('win'):
        update_path = Path(r'Z:/misc/testing/ATE/K2/zqchen/Program/boya_upload_test_file_sys')

    dcList = [
        update_path / 'pyLib',
        update_path / 'temp',
        update_path / 'perl',
        update_path / 'update_status.json'
    ]

    app_root_path = Path(__file__).resolve().parent

    def update_file(checkPath, relative_path=""):
        update_files = list(checkPath.glob('*'))
        if update_files:
            for file in update_files:
                if file in dcList:
                    continue
                elif file.is_file():
                    dest_path = app_root_path / relative_path / file.name
                    print(f'更新文件: {file}')
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        if dest_path.exists():
                            dest_path.unlink()
                    except PermissionError:
                        print(f"\"{dest_path}\" 删除失败，可能是权限问题")
                        continue
                    shutil.copy(file, dest_path)
                elif file.is_dir():
                    update_file(file, os.path.join(relative_path, file.name))
    if update_path != app_root_path:
        update_file(update_path, "")

@app.route('/restartSys')
def restartSys():
    if Path('/.dockerenv').exists():
        print("正在重启docker！")
        os._exit(0)
    else:
        python_executable = sys.executable
        new_process = Process(target=os.execv, args=(python_executable, [python_executable, Path(__file__)], ))
        new_process.start()
        return "restart"
        
def update_and_restart():
    global main_process_pid
    update_status = {"status": "updating"}
    with status_file_path.open("w", encoding="utf-8") as status_file:
        json.dump(update_status, status_file)
        
    python_executable = sys.executable
    current_script_filename = Path(__file__).stem
    command = f"from {current_script_filename} import updateFiles; updateFiles()"
    use_shell = True if sys.platform.startswith('win') else False
    print("开始更新系统...")
    result = subprocess.run([python_executable, '-c', command], capture_output=True, text=True, shell=use_shell)
    if result.stdout:
        print(f"\n{result.stdout}")
    if result.stderr:
        print(f"{result.stderr}")
    update_status = {"status": "update_complete", "main_process_pid": main_process_pid}
    with status_file_path.open("w", encoding="utf-8") as status_file:
        json.dump(update_status, status_file)
    print("系统更新完成，正在重启服务!")

@app.route('/check_update', methods=['GET'])
def check_update():
    if status_file_path.exists():
        with status_file_path.open("r", encoding="utf-8") as status_file:
            update_status = json.load(status_file)
        if update_status.get("status") != ("updating" and "update_complete"):
            with lock:
                update_and_restart()
            return jsonify({"status": "update_complete"})
        elif update_status.get("status") == "update_complete":
            return jsonify({"status": "update_complete"})
        elif update_status.get("status") == "updating":
            return jsonify({"status": "updating"})
    else:
        update_status = {"status": "unknown"}
        with status_file_path.open("w", encoding="utf-8") as status_file:
            json.dump(update_status, status_file)
    return jsonify({"status": "unknown"})

@app.route('/clear_files', methods=['POST'])
def clear_files():
    print('清除中...')
    if 'OutFileList' in session:
        del session['OutFileList']
    return jsonify(success=True)

@app.route('/aboutInfo')
def read_aboutInfo():
    with open(Path('static/about.txt'), 'r', encoding='utf-8') as flie:
        text = flie.read()
    return text

@app.route('/upload', methods=['POST'])
def upload():
    OutFileList = []
    filelist = []
    session['OutFileList'] = OutFileList
    session.pop('OutFileList', None)
    uploaded_files_list = request.files.getlist('files')
    uploaded_folders_list = request.files.getlist('folder')

    directory_structure = get_directory_structure(Path(f"temp/{request.headers.get('X-Real-IP', request.remote_addr)}")) if Path(f"temp/{request.headers.get('X-Real-IP', request.remote_addr)}").exists() else {}

    print("分析文件中，请耐心等待...")
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    temp_folder = Path('temp') / str(request.headers.get('X-Real-IP', request.remote_addr)) / current_time
    
    with lock:
        while temp_folder.exists():
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            temp_folder = Path('temp') / str(request.headers.get('X-Real-IP', request.remote_addr)) / current_time

        temp_folder.mkdir(parents=True, exist_ok=True)
    
    rmFileAndDir(temp_folder)

    uploaded_names = []

    # 处理上传的文件
    for file in uploaded_files_list:
        filename = file.filename
        if filename == '':
            continue
        file_path = temp_folder / filename
        file.save(file_path)
        if file_path.suffix == '.*':
            filelist.append(file_path)
        uploaded_names.append(filename)

    # 处理上传的文件夹
    for folder in uploaded_folders_list:
        if folder.filename == '':
            continue
        folder_path = temp_folder / folder.filename
        filepath, shotname, extension = get_filePath_fileName_fileExt(folder_path)
        filepath.mkdir(parents=True, exist_ok=True)
        folder.save(folder_path)
        get_filePath_list(folder_path, '.*', filelist)
        uploaded_names.append(folder.filename)

    log_content = '\n'.join(uploaded_names)
    log_filename = f"log_{current_time}.txt"
    log_file_path = temp_folder / log_filename

    # 存储用户选择的脚本名到session中
    selected_script_for_choose = request.form.get('scriptSelectorForChoose')
    if selected_script_for_choose:
        session['selected_script_for_choose'] = selected_script_for_choose
    
    try:
        if filelist:  # 确保filelist不为空
            temp_folder = filelist[0].parent

        last_modified_times = get_last_modified_times(temp_folder)
        print(f"开始执行脚本：{request.form.get('scriptSelectorForChoose')}，请等待...")

        if request.form.get('scriptSelectorForChoose').split('.')[-1] == 'pl':
            mainPathFlag = False
            def run_perl_script(file_path):
                command, use_shell = (r'C:\\Strawberry\perl\bin\perl.exe', True) if sys.platform.startswith('win') else ('perl', False)
                perl_run(Path('pyLib').resolve() / request.form.get('scriptSelectorForPath'), command, use_shell, file_path)
            for file_path in temp_folder.iterdir():
                if file_path.is_dir():
                    run_perl_script(file_path)
                elif file_path.is_file():
                    mainPathFlag = True
            if mainPathFlag:
                run_perl_script(temp_folder)
        elif request.form.get('scriptSelectorForChoose').split('.')[-1] == 'py':
            current_script_filename = Path(__file__).stem
            command = f"import sys; sys.path.append(r'{Path(__file__).parent}'); from {current_script_filename} import import_and_run; \
                        import_and_run(r'{Path('pyLib').resolve() / request.form.get('scriptSelectorForChoose')}', r'{temp_folder.resolve()}')"
            use_shell = True if sys.platform.startswith('win') else False
            # 使用 sys.executable 执行 Python 解释器
            result = subprocess.Popen([sys.executable, '-c', command], cwd=temp_folder.resolve(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=use_shell)
            print(f"脚本输出：")
            for line in result.stdout:
                print(line)
        new_files, modified_files, deleted_files = check_for_changes(temp_folder, last_modified_times)
        OutFileList = OutFileList + new_files + modified_files
    except Exception as e:
        print(f"脚本执行出错: {e}")
    finally:
        print(f"脚本 {request.form.get('scriptSelectorForChoose')} 执行结束！=================================")
   
    sid = (request.sid if hasattr(request, 'sid') else sids.get(request.args.get('sid', None), None)) if has_request_context() else None
    with log_file_path.open('w', encoding="utf-8") as log_file:
        if sid:
            for line in console_output[sid]:
                if isinstance(line, bytes):
                    log_file.write(line.decode('utf-8'))
                else:
                    log_file.write(line)
            console_output[sid].clear()
        log_file.write(log_content)


    print(log_file_path)
    OutFileList.append(str(log_file_path))

    # 保存 OutFileList 到 session
    session['OutFileList'] = OutFileList
    session['uploaded_files'] = uploaded_names

    # Redirect to another route to display the results
    # redirect_url = url_for('index', uploaded_files=uploaded_names, log_files=OutFileList)
    return render_template('index.html', log_entries='', log_files=OutFileList, uploaded_files=uploaded_names, no_files = 0, files_structure=directory_structure, py_scripts='default', selected_script_for_choose='default', selected_script_for_path='default',)

@app.route('/upload_by_path', methods=['POST'])
def upload_by_path():
    OutFileList = []
    if 'OutFileList' in session:
        del session['OutFileList']
    session['OutFileList'] = OutFileList
    file_path = request.form.get('manualFilePath')
    print("==================上传文件的完整路径为：" + file_path + "==================")
    print("温馨提示：您选择的是以网盘路径上传数据，生成的excel文件会直接放在网盘的同级别目录中！！！")
    print("分析文件中，请耐心等待...")
    # 修正Windows、macOS设备映射到linux服务器中的路径
    if sys.platform.startswith('linux'):
        if "Z:" in file_path:
            # 映射Windows路径
            file_path = file_path.replace("Z:", "/Z").replace("\\", "/")
        elif "/Volumes/fileserver" in file_path:
            # 映射macOS路径
            file_path = file_path.replace("/Volumes/fileserver", "/Z")
        print(f"映射到linux的路径为：{file_path}")

    if not file_path or not Path(file_path).exists():
        return jsonify({"error": "提供的路径不是有效的文件路径，请检查并重新输入！"}), 400

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    temp_folder = Path('temp') / str(request.headers.get('X-Real-IP', request.remote_addr)) / current_time

    with lock:
        while temp_folder.exists():
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            temp_folder = Path('temp') / str(request.headers.get('X-Real-IP', request.remote_addr)) / current_time

        temp_folder.mkdir(parents=True, exist_ok=True)
    
    rmFileAndDir(temp_folder)

    # filename = secure_filename(Path(file_path).name)
    filename = Path(file_path).name

    uploaded_names = [filename]
    # log_content = '\n'.join(uploaded_names)
    log_filename = f"log_{current_time}.txt"
    log_file_path = temp_folder / log_filename

    # 存储用户选择的脚本名到session中
    selected_script_for_path = request.form.get('scriptSelectorForPath')
    if selected_script_for_path:
        session['selected_script_for_path'] = selected_script_for_path

    try:
        last_modified_times = get_last_modified_times(file_path)
        print(f"开始执行脚本：{request.form.get('scriptSelectorForPath')}，请等待...")

        if request.form.get('scriptSelectorForPath').split('.')[-1] == 'pl':
            command, use_shell = (r'C:\\Strawberry\perl\bin\perl.exe', True) if sys.platform.startswith('win') else ('perl', False)
            perl_run(Path('pyLib').resolve() / request.form.get('scriptSelectorForPath'), command, use_shell, file_path)
        elif request.form.get('scriptSelectorForPath').split('.')[-1] == 'py':
            current_script_filename = Path(__file__).stem
            command = f"import sys; sys.path.append(r'{Path(__file__).parent}'); from {current_script_filename} import import_and_run; \
                        import_and_run(r'{Path('pyLib').resolve() / request.form.get('scriptSelectorForPath')}', r'{Path(file_path).resolve()}')"
            use_shell = True if sys.platform.startswith('win') else False
            # 使用 sys.executable 执行 Python 解释器
            result = subprocess.Popen([sys.executable, '-c', command], cwd=file_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=use_shell)
            print(f"脚本输出：")
            for line in result.stdout:
                print(line)
        new_files, modified_files, deleted_files = check_for_changes(file_path, last_modified_times)
        OutFileList = OutFileList + new_files + modified_files
    except Exception as e:
        print(f"脚本执行出错: {e}")
    finally:
        print(f"脚本 {request.form.get('scriptSelectorForPath')} 执行结束！=================================")
    
    if Path(file_path).is_dir():
        shutil.copytree(Path(file_path), temp_folder / Path(file_path).name)

    sid = (request.sid if hasattr(request, 'sid') else sids.get(request.args.get('sid', None), None)) if has_request_context() else None
    with log_file_path.open('w', encoding="utf-8") as log_file:
        if sid:
            for line in console_output[sid]:
                log_file.write(line)
            console_output[sid].clear()
        log_file.write(filename)

    OutFileList.append(str(log_file_path))

    # OutFileList = [Path(file) for file in OutFileList]

    session['OutFileList'] = OutFileList
    session['uploaded_files'] = uploaded_names
    
    # redirect_url = url_for('index', uploaded_files=uploaded_names, log_files=OutFileList)
    # redirect_url = url_for('index')
    # return jsonify({"redirect": redirect_url})
    directory_structure = get_directory_structure(Path(f"temp/{request.headers.get('X-Real-IP', request.remote_addr)}")) if Path(f"temp/{request.headers.get('X-Real-IP', request.remote_addr)}").exists() else {}

    return render_template('index.html', log_entries='', log_files=OutFileList, uploaded_files=uploaded_names, no_files = 0, files_structure=directory_structure, py_scripts='default', selected_script_for_choose='default', selected_script_for_path='default',)

@app.route('/manage_scripts', methods=['POST'])
def manage_scripts():
    files_to_delete = json.loads(request.form.get('delete_files'))
    print(f"预备删除的脚本：{files_to_delete}")
    # try:
    uploaded_files = request.files.getlist('upload_files')
    print(f"预备上传的脚本：{uploaded_files}")
    
    try:
        # 删除脚本
        for file in files_to_delete:
            Path(f"pyLib/{file}").unlink()
            print('移除脚本操作成功，脚本列表将在3s之后自动刷新！！！')
        
        # 上传脚本
        for file in uploaded_files:
            if file.filename.split('.')[-1] == ('py'):
                file.save(f"pyLib/{file.filename}")
                print(f'脚本<{file.filename}>上传成功，脚本列表将在3s之后自动刷新！！！')
            elif file.filename.split('.')[-1] == ('pl'):
                file.save(f"pyLib/{file.filename}")
                print(f'脚本<{file.filename}>上传成功，脚本列表将在3s之后自动刷新！！！')
            else: 
                print('操作失败，您上传的不是py或者pl脚本，页面将在3s之后自动刷新！！！')
                break
        return render_template('index.html')
    except Exception as e: 
        return jsonify(success=False, error=str(e))
    
if __name__ == '__main__':
    sys.stdout.write = wrapper_write
    main_process_pid = os.getpid()
    print('当前进程：', main_process_pid)
    try:
        with status_file_path.open("r", encoding="utf-8") as status_file:
            update_status = json.load(status_file)
        pid_to_check = update_status.get("main_process_pid") or None
        if update_status.get("status") == "update_complete" and pid_to_check != None and psutil.pid_exists(pid_to_check) and not Path('/.dockerenv').exists():
            try:
                process = psutil.Process(pid_to_check)
                process.terminate()
                print(f"进程 {pid_to_check} 已终止")
            except psutil.NoSuchProcess:
                print(f"进程 {pid_to_check} 不存在")
            except psutil.AccessDenied:
                print(f"无法终止进程 {pid_to_check}，权限不足")
    finally:
        with status_file_path.open("w", encoding="utf-8") as status_file:
            json.dump({"status": "None"}, status_file)

    # 判断服务器系统，执行挂载指令，我们打算把项目部署到docker中
    if sys.platform.startswith('linux'):
        command = ["sudo", "mount", "-t", "cifs", "//192.168.2.108/fileserver", "/Z", "-o", "credentials=/credentials/info.txt,vers=3.0,sec=ntlmssp,iocharset=utf8"]
        subprocess.run(command, capture_output=True, text=True)
    scheduler = BackgroundScheduler()
    scheduler.add_job(rmFileAndDir, 'cron', hour=4, minute=0, args=[Path('temp')])
    scheduler.add_job(deleteOldestFolder, 'interval', minutes=15, args=[Path('temp')])
    scheduler.start()
    socketio.run(app, debug=True, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True, use_reloader=False, log_output=False)