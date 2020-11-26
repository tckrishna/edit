from flask import Response, render_template, request, redirect, url_for, json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user, login_required, login_user, logout_user
import threading
import os
import PIL

from server import app

limiter = Limiter(app, key_func=get_remote_address)

from server.db import db
from server.utils import scores, rotate, socketio
from server.login import login_manager

# ----- AUTHENTICATION ----
@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("3/minute;20/day")
def login():
    # Check if an user is already logged in.
    if current_user.is_authenticated:
        return redirect(url_for('map'))
    # Handle received forms
    if request.method == 'POST':
        user_id = request.form['user']
        user_pass = request.form['pass']
        user = login_manager.get_user(user_id, user_pass)
        if user is not None:
            login_user(user, remember=True)
            return redirect(request.args.get("next") or url_for("map"))
    
    return render_template('login.html')


@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('map'))

# ----- WEB PAGES -----
@app.route('/scan', methods=['GET'])
@login_required
def scan():
    return render_template('scan.html')


@app.route('/audio', methods=["GET"])
@login_required
def audio():
    return render_template('audio.html')


@app.route('/location', methods=["GET"])
@login_required
def location():
    return render_template('location.html')


@app.route('/map', methods=["GET"])
def map():
    return render_template('map.html')


@app.route('/upload', methods=["GET"])
def upload():
    return render_template('upload.html')

# ----- AJAX -----
# Upload scan image
@app.route('/put_scan', methods=['POST'])
@login_required
def put_scan():
    rotation = request.form.get("rotation", None, type=int)
    lang = request.form.get("lang", None, type=str)
    name = request.form.get("name", None, type=str)
    email = request.form.get("email", None, type=str)
    phone = request.form.get("phone", None, type=str)
    date = request.form.get("date", None, type=str)
    bedrijf = request.form.get("bedrijf", None, type=str)
    teelt = request.form.get("teelt", None, type=str)
    fotographer = request.form.get("fotographer", None, type=str)
    desc = request.form.get("desc", None, type=str)
    

    # Convert empty to None
    if email == "": email = None
    if phone == "": phone = None
    if date == "": date = None
    if bedrijf == "": bedrijf = None
    if teelt == "": teelt = None
    if fotographer == "": fotographer = None
    if desc == "": desc = None
    
    # Check if file, rotation and language ok
    if len(request.files) == 1 and rotation is not None and rotation >= 0 and rotation < 360 and lang in ['nl', 'en'] and name is not None and (phone is not None or email is not None):
        file = list(request.files.values())[0]
        extension = os.path.splitext(file.filename)[1]

        # Only accept jpeg
        if extension in ['.jpg', '.jpeg']:
            # Rotate
            file = rotate.rotate_img(file, -rotation)

            id = db.insertScan(lang, name, email, phone, date, bedrijf, teelt, fotographer, desc)

            # Makes image available over /static/uploads/scans/[id].jpg
            f_path = "./server/web/static/uploads/scans/{}.jpg".format(id)
            file.save(f_path)

            # Generate task to get score and store in db
            task = threading.Thread(target=scores.aes_vector_sim_score, args=(id,))
            task.start()

            # Emit event over socket
            socketio.sendMessage('audio_ready', {'id': id}, namespace='/audio')

            # Return id in json format
            return Response(response=json.dumps({'id': id}), status=200, mimetype='application/json')

    # 400 = Bad request
    return Response(response=None, status=400)

# Return the next scan to add audio to
@app.route("/get_audio_id", methods=["GET"])
@login_required
def get_audio_id():
    id, lang = db.getScanReadyAudio()
    return Response(response=json.dumps({'id': id, 'lang': lang}), status=200, mimetype='application/json')

# Upload audio file
@app.route("/put_audio", methods=["POST"])
@login_required
def put_audio():
    id = request.form.get("id", None, type=int)

    # Check if id exists and right state (getScanState returns None when id doesn't exist)
    if id is not None and db.getScanState(id) == 'ready_audio':

        if len(request.files) == 0:
            db.updateScanState(id, 'ready_loc')
            db.updateScanAudio(id, False)

            # Emit event over socket
            socketio.sendMessage('loc_ready', {'id': id}, namespace='/loc')
            socketio.sendMessage('audio_submit', {'id': id}, namespace='/audio') # Keep consistent state over all audio pages
            
            # Return id in json format
            return Response(response=json.dumps({'id': id}), status=200, mimetype='application/json')

        elif len(request.files) == 1:
            file = list(request.files.values())[0]
            extension = os.path.splitext(file.filename)[1]

            # Only accept .wav
            if extension == '.wav':
                db.updateScanState(id, 'ready_loc')
                db.updateScanAudio(id, True)

                # Makes audio available over /static/uploads/audio/[id].wav
                f_path = "./server/web/static/uploads/audio/{}.wav".format(id)
                file.save(f_path)

                # Emit event over socket
                socketio.sendMessage('loc_ready', {'id': id}, namespace='/loc')
                socketio.sendMessage('audio_submit', {'id': id}, namespace='/audio') # Keep consistent state over all audio pages

                # Return id in json format
                return Response(response=json.dumps({'id': id}), status=200, mimetype='application/json')

    # 400 = Bad request
    return Response(response=None, status=400)

# Return the next scan to add audio to
@app.route("/get_loc_id", methods=["GET"])
@login_required
def get_loc_id():
    id, lang = db.getScanReadyLoc()
    return Response(response=json.dumps({'id': id, 'lang': lang}), status=200, mimetype='application/json')

# Upload location
@app.route("/put_loc", methods=["POST"])
@login_required
def put_loc():
    id = request.form.get("id", None, type=int)
    lat = request.form.get("lat", None, type=float)
    lng = request.form.get("lng", None, type=float)

    # Check if id exists and right state (getScanState returns None when id doesn't exist)
    if id is not None and db.getScanState(id) == 'ready_loc':

        if lat is not None and lng is not None:
            db.updateScanState(id, 'done')
            db.updateScanLoc(id, lat, lng)

            # Generate task to get score and store in db
            task = threading.Thread(target=scores.loc_total_score, args=(id,))
            task.start()

            # Emit event over socket
            socketio.sendMessage('map_ready', {'id': id}, namespace='/map')
            socketio.sendMessage('loc_submit', {'id': id}, namespace='/loc') # Keep consistent state over all location pages

            # Return id in json format
            return Response(response=json.dumps({'id': id}), status=200, mimetype='application/json')

        elif lat is None and lng is None:
            db.updateScanState(id, 'canceled')

             # Emit event over socket
            socketio.sendMessage('loc_submit', {'id': id}, namespace='/loc') # Keep consistent state over all location pages
            
            # Return id in json format
            return Response(response=json.dumps({'id': id}), status=200, mimetype='application/json')

    # 400 = Bad request
    return Response(response=None, status=400)

# Return all locations done scans
@app.route("/get_scans_loc", methods=["GET"])
def get_scans_loc():
    data = {}
    for scan in db.getScansLoc():
        data[scan[0]] = {'lat': scan[1], 'lng': scan[2]}
    return Response(response=json.dumps(data), status=200, mimetype='application/json')

# Return top aes done scans
@app.route("/get_scans_top_aes_today", methods=["POST"])
def get_scans_top_aes_today():
    limit = request.form.get("limit", None, type=int)
    if limit is not None:
        scans = db.getScansTopAesToday(limit)
        data = []
        if len(scans) > 0:
            for scan in scans:
                data.append({'id': scan[0], 'aes_score': scan[1]})
        else:
            data = None
        return Response(response=json.dumps(data), status=200, mimetype='application/json')

    # 400 = Bad request
    return Response(response=None, status=400)

# Return top total done scan
@app.route("/get_scans_top_total_today", methods=["POST"])
def get_scans_top_total_today():
    limit = request.form.get("limit", None, type=int)
    if limit is not None:
        scans = db.getScansTopTotalToday(limit)
        data = []
        if len(scans) > 0:
            for scan in scans:
                data.append({'id': scan[0], 'total_score': scan[1]})
        else:
            data = None
        return Response(response=json.dumps(data), status=200, mimetype='application/json')

    # 400 = Bad request
    return Response(response=None, status=400)

# Return top total done scan previous day
@app.route("/get_scans_top_total_yesterday", methods=["POST"])
def get_scans_top_total_yesterday():
    limit = request.form.get("limit", None, type=int)
    if limit is not None:
        scans = db.getScansDoneTopTotalYesterday(limit)
        data = []

        if len(scans) > 0:
            for scan in scans:
                data.append({'id': scan[0], 'total_score': scan[1]})
        else:
            data = None
        return Response(response=json.dumps(data), status=200, mimetype='application/json')

    # 400 = Bad request
    return Response(response=None, status=400)

# Upload from file
@app.route("/put_upload", methods=["POST"])
@limiter.limit("30/minute;1000/day")
def put_upload():
    lang = request.form.get("lang", None, type=str)
    lat = request.form.get("lat", None, type=float)
    lng = request.form.get("lng", None, type=float)
    name = request.form.get("name", None, type=str)
    email = request.form.get("email", None, type=str)
    phone = request.form.get("phone", None, type=str)
    date = request.form.get("date", None, type=str)
    bedrijf = request.form.get("bedrijf", None, type=str)
    teelt = request.form.get("teelt", None, type=str)
    fotographer = request.form.get("fotographer", None, type=str)
    desc = request.form.get("desc", None, type=str)
    

    # Convert empty to None
    if email == "": email = None
    if phone == "": phone = None
    if date == "": date = None
    if bedrijf == "": bedrijf = None
    if teelt == "": teelt = None
    if fotographer == "": fotographer = None
    if desc == "": desc = None

    # Check lang, scan, loc
    if len(request.files) in [1, 2] and lang in ['nl', 'en'] and lat is not None and lng is not None and name is not None and email is not None:

        scan_file = None
        audio_file = None
        # Assign files (if 2 scan files last one will be saved)
        for file in list(request.files.values()):
            extension = os.path.splitext(file.filename)[1]
            if extension in ['.jpg', '.jpeg', '.JPG']:
                scan_file = file
            elif extension == '.wav':
                audio_file = file

        if scan_file is not None:
            # Save to db
            id = db.insertScan(lang, name, email, phone, date, bedrijf, teelt, fotographer, desc)
            db.updateScanAudio(id, (audio_file is not None))
            db.updateScanLoc(id, lat, lng)
            db.updateScanState(id, 'done')

            # Makes image available over /static/uploads/scans/[id].jpg
            f_scan_path = "./server/web/static/uploads/scans/{}.jpg".format(id)
            scan_file.save(f_scan_path)

            if audio_file is not None:
                # Makes audio available over /static/uploads/audio/[id].wav
                f_audio_path = "./server/web/static/uploads/audio/{}.wav".format(id)
                audio_file.save(f_audio_path)

            # Generate task to get score and store in db
            task = threading.Thread(target=scores.aes_vector_sim_loc_total_score, args=(id,))
            task.start()

            # Return id in json format
            return Response(response=json.dumps({'id': id}), status=200, mimetype='application/json')

    # 400 = Bad request
    return Response(response=None, status=400)

@app.route("/get_metadata", methods=["POST"])
def get_metadata():
    id = request.form.get("id", None, type=int)
    if id is not None:
        scans = db.getMetadata(id)
        data = []
        if len(scans) > 0:
            for scan in scans:
                data.append({'name': "Iemand" if scan[0] is None else scan[0], 'date': "Onbekend" if scan[1] is None else scan[1], 'description': "niet beschikbaar" if scan[2] is None else scan[2]})
        else:
            data = None
        return Response(response=json.dumps(data[0]), status=200, mimetype='application/json')

    # 400 = Bad request
    return Response(response=None, status=400)
