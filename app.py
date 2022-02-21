from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename

import os
import hashlib
import shutil

from datetime import datetime, timedelta

app = Flask(__name__)
# session 관리키
app.secret_key = "FLAGSHIP"
# 파일 업로드 경로 설정(local)
app.config["IMAGE_UPLOADS"] = "/static/images"
# 이미지 파일 패스
img_filepath = 'static/images/'

client = MongoClient(
    'mongodb+srv://admin:admin@cluster0.cs5sa.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.toy

# 랜딩 페이지


@app.route('/')
def index():
    # 세션 정보가 있으면 메인 페이지로 리다이렉팅
    if 'userId_session' in session:
        return redirect(url_for('main'))
    # 세션 정보가 없으면 로그인 페이지로 렌더링
    else:
        return render_template('login.html')

# 메인 페이지


@app.route('/main')
def main():
    # 세션 정보가 있으면 메인 페이지로 렌더링
    if 'userId_session' in session:
        # cookie 정보 획득
        request.cookies.get('cookie_info')
        return render_template('main.html')
    # 세션 정보가 없으면 로그인 페이지로 렌더링
    else:
        return render_template('login.html')

# 로그인


@app.route('/login_check', methods=["GET", "POST"])
def login():
    # request method가 POST인 경우
    if request.method == 'POST':
        userId_receive = request.form['id_give']
        userPassword_receive = request.form['password_give']
        pw_hash = hashlib.sha256(
            userPassword_receive.encode('utf-8')).hexdigest()

        # 아이디가 존재하는지 조회 후 없으면 result, msg 리턴
        if db.users.find_one({'user_id': userId_receive}) is None:
            return jsonify({'result': 'fail', 'msg': '아이디가 존재하지 않습니다.'})

        # 아이디가 존재하는 경우, 아이디 및 비밀번호가 일치하는지 조회
        result = db.users.find_one(
            {'user_id': userId_receive, 'user_password': pw_hash})
        # 아이디 및 패스워드가 일치하는 데이터가 존재하면 아래 처리 실행
        if result is not None:
            # session에 user아이디 값 저장
            session["userId_session"] = userId_receive

            cookie_info = userId_receive  # cookie 저장
            resp = make_response()  # 쿠키값 설정을 위해 make_response를 사용
            resp.set_cookie('cookie_info', cookie_info)  # 쿠키 저장

            # 유저 정보 획득
            user = db.users.find_one({'user_id': userId_receive})
            # 유저 프로필 이미지 정보 획득
            profile = db.profile.find(
                {'profile_no': user['profile_no']}, {'_id': False})
            # 최근 이미지 정보만 획득 후 RETURN
            lastest_profile = sorted(
                profile, key=lambda k: k['profile_no'])[-1]
            # 세션에 유저 최신 프로필 이미지 파일명 저장
            session["converted_filename"] = lastest_profile['converted_filename']
            # result : success 리턴
            return jsonify({'result': 'success'})
        # 아이디 및 패스워드가 일치하지 않는 경우 result, msg 리턴
        else:
            return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
    # 잘못된 접근 차단
    else:
        return '잘못된 접근입니다.'

# 회원가입 페이지 렌더링


@app.route('/signup_render')
def signup_render():
    return render_template('signup.html')

# 회원가입


@app.route('/signup', methods=["POST"])
def signup_post():
    # [유저 고유번호 부여]
    # users의 전체 데이터 조회
    all_users = list(db.users.find({}, {'_id': False}))
    # 람다함수를 이용, user_id컬럼을 key로 오름차순 정렬 후 [-1]로 마지막 요소 추출
    lastest_user = sorted(all_users, key=lambda k: k['user_no'])[-1]
    # 마지막 등록된 유저의 user_no에 1 증산 후 user_no 부여
    user_no = lastest_user['user_no'] + 1

    # [유저 아이디]
    id_receive = request.form['id_give']
    # 아이디 중복검사 진행
    if duplicate_chk(id_receive):
        return jsonify({'result': 'fail', 'msg': '아이디 중복, 다시 입력해주세요.'})

    # [유저 패스워드]
    password_receive = request.form['password_give']
    # 해시함수로 패스워드 복호화 진행
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()

    doc = {
        'user_no': user_no,  # 유저 고유번호
        'user_id': id_receive,  # 유저 ID
        'user_password': password_hash,  # 유저 패스워드(복호화된 것)
        'profile_no': 0  # 기본 프로필 이미지 No=0 등록
    }
    db.users.insert_one(doc)

    # 기본 프로필 이미지 DB에 등록
    doc = {
        'profile_no': 0,  # Default값 0
        # 기본 프로필 이미지 파일명 (로컬 statc/images폴더에 저장되어 있음)
        'file_name': 'basic_profile_img.png',
        'upload_timestamp': '',  # 업로드 시간은 비워둠
        'converted_filename': 'basic_profile_img.png',  # 기본 프로필 이미지는 변환하지 않으므로 파일명 그대로 둠
        'file_path': 'static/images/',  # 기본 프로필 이미지 파일 패스
        'user_id': id_receive  # 유저 ID
    }
    db.profile.insert_one(doc)

    # 회원 가입 완료 후, result, msg 리턴
    return jsonify({'result': 'success', 'msg': '회원 가입이 완료되었습니다.'})

# 아이디 중복체크 (매개변수=유저가 입력한 ID값)


def duplicate_chk(id_receive):
    # 유저가 입력한 ID값으로 users DB에 중복되는 값이 있는지 확인 후 리턴 (리턴되는 값 True 또는 False)
    exists = bool(db.users.find_one({"user_id": id_receive}))
    return exists

# 회원정보수정


@app.route('/userprofile')
def user_profile():
    # 세션 정보가 있으면 회원정보 수정 페이지로 렌더링
    if 'userId_session' in session:
        return render_template('editprofile.html')
    # 세션 정보가 없으면 랜딩 페이지로 이동
    else:
        return redirect('/')


@app.route('/userpassword')
def user_password():
    # 세션 정보가 있으면 회원정보 수정 페이지로 렌더링
    if 'userId_session' in session:
        return render_template('editpassword.html')
    # 세션 정보가 없으면 랜딩 페이지로 이동
    else:
        return redirect('/')

# 파일 업로드(local)


@app.route('/file_upload', methods=["POST"])
def upload_file():
    # 세션 정보가 있으면 처리 실행
    if 'userId_session' in session:
        # 프로필 사진을 선택한 경우 업로드 처리 실행
        if request.files:
            # 이미지 파일 변수에 저장
            f = request.files['file']
            # 파일명 보호 및 로컬 서버에 저장
            original_filename = secure_filename(f.filename)
            # 원본 파일 저장
            save_file = img_filepath + original_filename
            f.save(save_file)

            # 원본 파일명 확장자 분리
            split_file = original_filename.split('.')
            # 새 파일명 명명 [명명 규칙: 원본 파일명 + 파일 업로드 시간 + 확장자]
            # 현재 시간 획득(파일명 변환용) 밀리 초(초 뒤에 소수점 이하 3자리)까지
            now = datetime.now()
            current_time = now.strftime("%Y%H%M%S%f")[:-3]
            converted_filename = split_file[0] + \
                '_' + current_time + '.' + split_file[1]

            # 파일명 변환
            path_old_filename = os.path.join(
                'static/images', original_filename)
            path_chg_filename = os.path.join(
                'static/images', converted_filename)
            shutil.move(path_old_filename, path_chg_filename)
            files = os.listdir('static/images/')

            # users DB에서 로그인한 유저 정보 조회
            user = db.users.find_one(
                {'user_id': session.get('userId_session')}, {'_id': False})
            # 유저의 프로필 고유번호에 1 증산하여 고유번호 변경
            profile_no = user['profile_no'] + 1
            doc = {
                'profile_no': profile_no,  # 프로필 이미지 고유번호
                'file_name': original_filename,  # 원본 파일명
                'upload_timestamp': current_time,  # 업로드 시간
                'converted_filename': converted_filename,  # 변환된 파일명
                'file_path': img_filepath,  # 파일 패스
                'user_id': session.get('userId_session')  # 유저 ID
            }
            db.profile.insert_one(doc)
            # 프로필 이미지를 profile DB에 업로드후 result, upload_flag 리턴
            return jsonify({'result': 'success', 'upload_flag': 'y'})
        # 프로필 이미지를 선택하지 않은 경우 업로드 처리하지 않고 result, upload_flag 리턴
        else:
            return jsonify({'result': 'success', 'upload_flag': 'n'})
    # 세션 정보가 없으면 로그인 화면으로 렌더링
    else:
        return render_template('login.html')

# 회원정보 수정


@app.route('/edit', methods=["POST"])
def edit_user_info():
    # 세션 정보가 존재하는 경우
    if 'userId_session' in session:
        # session에서 user_id 획득
        user_id = session.get('userId_session')
        # User가 폼에 입력한 Password를 Hash함수로 복호화
        password_receive = request.form['inputPw_give']
        # 변경할 비밀번호
        change_password = request.form['changePw_give']
        # Password를 입력한 경우
        if password_receive != '':
            # 해시함수로 패스워드 복호화
            password_hash = hashlib.sha256(
                password_receive.encode('utf-8')).hexdigest()
        # 패스워드와 변경할 패스워드가 입력된 경우만 실행
        if password_receive != '' and change_password != '':
            # ID를 key로 DB에서 User객체 획득
            user = db.users.find_one(
                {'user_id': user_id, 'user_password': password_hash})
            if user is not None:
                # 복호화된 기존 비밀번호 획득
                current_password = user['user_password']
                # 변경할 비밀번호 Hash함수로 복호화
                change_password_hash = hashlib.sha256(
                    change_password.encode('utf-8')).hexdigest()
                # 현재 (복호화 된)비밀번호와 복호화 된 변경할 비밀번호 값이 같은 경우 result, msg 리턴
                if password_hash == change_password_hash:
                    return jsonify({'result': 'fail', 'msg': '현재 비밀번호와 다른 비밀번호를 입력해주세요.'})
                # "DB에 저장된 비밀번호"와 유저가 입력한 "현재 비밀번호"가 일치하면 비밀번호 변경 및 프로필 이미지 등록
                if password_hash == current_password:
                    # 프로필 이미지 DB에서 유저 아이디가 일치하는 전체 데이터 조회
                    images = list(db.profile.find(
                        {'user_id': user_id}, {'_id': False}))
                    # 람다함수를 이용, profile_no컬럼을 key로 오름차순 정렬 후 [-1]로 마지막 요소 추출
                    lastest_profile_no = sorted(
                        images, key=lambda k: k['profile_no'])[-1]
                    # user DB에서 현재 유저의 비밀번호 및 프로필 이미지 고유번호를 업데이트
                    db.users.update_one(
                        {'user_id': user_id},
                        {'$set': {
                            'user_password': change_password_hash,
                            'profile_no': lastest_profile_no['profile_no']
                        }}
                    )
                    # 변경 전 프로필 이미지 파일을 로컬에서 삭제 (변경 전 이미지가 기본 프로필 이미지가 아닌 경우)
                    if images[len(images)-2]['profile_no'] != 0:
                        delete_filename = img_filepath + \
                            images[len(images) - 2]['converted_filename']
                        # 로컬에 해당 파일이 있는지 확인 후 삭제
                        if os.path.isfile(delete_filename):
                            os.remove(delete_filename)
                    # session 강제 만료
                    session.pop("userId_session", None)
                    return jsonify({'result': 'success', 'msg': '비밀번호가 정상적으로 변경되었습니다.', 'pw_ch_flag': 'y'})
            # "DB에 저장된 비밀번호"와 유저가 입력한 "현재 비밀번호"가 일치하지 않는 경우 result, msg 리턴
            else:
                return jsonify({'result': 'fail', 'msg': '비밀번호를 다시 확인해주세요.'})
        # 패스워드는 변경하지 않고 프로필 이미지만 변경하려는 경우
        else:
            # 프로필 이미지 DB에서 유저 아이디가 일치하는 전체 데이터 조회
            images = list(db.profile.find(
                {'user_id': user_id}, {'_id': False}))
            # 람다함수를 이용, profile_no컬럼을 key로 오름차순 정렬 후 [-1]로 마지막 요소 추출
            lastest_profile_no = sorted(
                images, key=lambda k: k['profile_no'])[-1]
            db.users.update_one({'user_id': user_id}, {
                                '$set': {'profile_no': lastest_profile_no['profile_no']}})

            # 변경 전 프로필 이미지 파일을 로컬에서 삭제 (변경 전 이미지가 기본 프로필 이미지가 아닌 경우)
            if images[len(images) - 2]['profile_no'] != 0:
                delete_filename = img_filepath + \
                    images[len(images) - 2]['converted_filename']
                # 로컬에 해당 파일이 있는지 확인 후 삭제
                if os.path.isfile(delete_filename):
                    os.remove(delete_filename)

            # 유저 정보 획득
            user = db.users.find_one({'user_id': session["userId_session"]})
            # 유저 프로필 이미지 정보 획득
            profile = db.profile.find(
                {'profile_no': user['profile_no']}, {'_id': False})
            # 최근 이미지 정보만 획득 후 RETURN
            lastest_profile = sorted(
                profile, key=lambda k: k['profile_no'])[-1]
            # 세션에 유저 최신 프로필 이미지 파일명 저장
            session["converted_filename"] = lastest_profile['converted_filename']

            return jsonify({'result': 'success', 'msg': '프로필 이미지가 정상적으로 변경되었습니다.', 'pw_ch_flag': 'n'})
    # 세션이 만료된 경우 로그인 페이지로 렌더링
    else:
        return render_template('login.html')

# 즐겨찾기


@app.route('/star')
def favorites():
    return render_template('favorites.html')

# 로그아웃


@app.route('/logout')
def logout():
    # session 강제 만료 후 '/'로 리다이렉팅
    session.pop("userId_session", None)
    return redirect('/')

# session 수명


@app.before_request
def make_session_permanent():
    session.permanent = True  # False인 경우 31일동안 보관
    app.permanent_session_lifetime = timedelta(
        minutes=30)  # session 수명을 5분간 유지
    # 김지호 : 잠시 30분으로 연장 좀 하겠습니다


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
