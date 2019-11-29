from flask import Flask, render_template, request, session, flash, redirect, url_for
from SRT.SRT.srt import SRT
from SRT.SRT.errors import SRTLoginError
from SRT.SRT.constants import STATION_CODE
from datetime import datetime
import os
app = Flask(__name__)
app.secret_key = os.urandom(16)


@app.route('/find')
def find():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('find.html', regions=list(STATION_CODE.keys()))


@app.route('/index', methods=['POST', 'GET'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form['dep'] == '' or request.form['arr'] == '':
            return 404, "출발역 또는 도착역 선택이 잘못되었습니다."
        session['dep'] = request.form['dep']
        session['arr'] = request.form['arr']
    elif 'dep' not in session or 'arr' not in session:
        return redirect(url_for('find'))
    srt = SRT(srt_id=session['username'], srt_pw=session['password'])
    trains = srt.search_train(
        dep=session['dep'],
        arr=session['arr'],
        available_only=False,
        time=datetime.now().strftime("%H%M%S")
    )
    return render_template('index.html', trains=trains)


@app.route('/reserve', methods=['POST', 'GET'])
def reserve():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        result = int(request.args.get('index'))
        srt = SRT(srt_id=session['username'], srt_pw=session['password'])
        trains = srt.search_train(
            dep=session['dep'],
            arr=session['arr'],
            available_only=False,
            time=datetime.now().strftime("%H%M%S")
        )
        srt.reserve(train=trains[result], auto_reserve=True)
        return render_template('success.html')
    return 404


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        return redirect(url_for('find'))
    if request.method == 'GET':
        return render_template('login.html', session=session)
    else:
        _id = request.form['username']
        pwd = request.form['password']
        try:
            srt = SRT(srt_id=_id, srt_pw=pwd)
            session['username'] = _id
            session['password'] = pwd
            return redirect(url_for('find'))
        except SRTLoginError as e:
            flash('Wrong login information')
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    session.pop('dep', None)
    session.pop('arr', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='localhost', port=5000, debug=True)
