import os
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
socketio = SocketIO(app)

rooms = {"main": []}

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)

    if username not in rooms[room]:
        rooms[room].append(username)
    emit('update_users', rooms[room], room=room)
    emit('message', {'username': 'System', 'message': f"{username} has joined the room."}, room=room)

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)

    if username in rooms[room]:
        rooms[room].remove(username)
    emit('update_users', rooms[room], room=room)
    emit('message', {'username': 'System', 'message': f"{username} has left the room."}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    emit('message', {'username': data['username'], 'message': data['message']}, room=room)

@socketio.on('upload_photo')
def handle_upload_photo(data):
    username = data['username']
    room = data['room']
    photo = data['photo']
    filename = data['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # Save the photo
    with open(filepath, 'wb') as f:
        f.write(photo)
    # Broadcast the photo URL
    emit('photo', {'username': username, 'photo_url': f"/uploads/{filename}"}, room=room)

@socketio.on('upload_audio')
def handle_upload_audio(data):
    username = data['username']
    room = data['room']
    audio = data['audio']
    filename = data['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # Save audio
    with open(filepath, 'wb') as f:
        f.write(audio)
    # Broadcast the audio URL
    emit('audio', {'username': username, 'audio_url': f"/uploads/{filename}"}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
