from flask import Flask, request, jsonify, render_template_string, session
import requests
import base64
import random
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "keneviz_secret_key_2026"

ADMIN_KEY = "devkeneviz"

# ============ VERİTABANLARI ============
APIS_DB = {
    1: {
        "name": "WEB ANALİZ",
        "endpoint": "https://kenevizwebmsapi.vercel.app/analyze",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Website detaylı analiz • Başlık, meta, resimler",
        "response_type": "json",
        "icon": "🔍"
    },
    2: {
        "name": "HIZ TESTİ",
        "endpoint": "https://kenevizwebmsapi.vercel.app/analyze",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Yüklenme süresi • 3 kez test • Ortalama",
        "response_type": "json",
        "icon": "⚡"
    },
    3: {
        "name": "SİTE BİLGİ",
        "endpoint": "https://kenevizindexcekenapi.vercel.app/index",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Header, encoding, yönlendirmeler",
        "response_type": "json",
        "icon": "ℹ️"
    },
    4: {
        "name": "SAĞLIK KONTROL",
        "endpoint": "https://kenevizwebmsapi.vercel.app/analyze",
        "params": {"url": ""},
        "method": "GET",
        "desc": "API durumu • Zaman damgası",
        "response_type": "json",
        "icon": "🏥"
    },
    5: {
        "name": "PİNG TESTİ",
        "endpoint": "https://kenevizurlipcekiciapi.vercel.app/urlipcek",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Bağlantı testi • Gecikme süresi",
        "response_type": "json",
        "icon": "📶"
    },
    6: {
        "name": "API BİLGİ",
        "endpoint": "https://kenevizwebmsapi.vercel.app/analyze",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Tüm endpoint'ler • API durumu",
        "response_type": "json",
        "icon": "🏠"
    },
    7: {
        "name": "GÖRSEL ÜRET",
        "endpoint": "https://kenevizimagegenerate.vercel.app/api/generate",
        "params": {"prompt": ""},
        "method": "GET",
        "desc": "Yapay zeka ile görsel oluştur",
        "response_type": "image",
        "icon": "🎨"
    },
    8: {
        "name": "SES SENTEZ",
        "endpoint": "https://kenevizttsapi.vercel.app/api/tts",
        "params": {"text": "", "lang": "tr"},
        "method": "GET",
        "desc": "Metni sese dönüştür",
        "response_type": "audio",
        "icon": "🎵"
    },
    9: {
        "name": "AYAK SORGU",
        "endpoint": "https://kenevizayaksorguapi.vercel.app/api/sorgula",
        "params": {"tgnick": "", "yas": ""},
        "method": "GET",
        "desc": "Kullanıcı bilgisi sorgula",
        "response_type": "json",
        "icon": "👤"
    }
}

VISITOR_COUNT = 0
ACTIVE_USERS = {}
ANNOUNCEMENTS = []
API_USAGE = {}

def generate_api_id():
    new_id = random.randint(10, 999)
    while new_id in APIS_DB:
        new_id = random.randint(10, 999)
    return new_id

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KENEVİZ • WEB SORGULAMA SİSTEMİ</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #f5f0ff 0%, #fce4ec 50%, #e8eaf6 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .logo {
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(135deg, #9b59b6, #e91e63, #6c5ce7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        }
        .logo span {
            font-size: 0.5em;
            background: none;
            -webkit-text-fill-color: #888;
        }
        .subtitle {
            color: #6c5ce7;
            margin-top: 10px;
            font-size: 0.85em;
        }

        /* Stats Bar */
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .stat-card {
            background: white;
            border-radius: 20px;
            padding: 15px 30px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            min-width: 150px;
        }
        .stat-card h3 {
            color: #e91e63;
            font-size: 0.7em;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .stat-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #6c5ce7;
        }

        /* Announcement */
        .announcement {
            background: linear-gradient(135deg, #9b59b6, #e91e63);
            border-radius: 15px;
            padding: 15px 25px;
            margin-bottom: 30px;
            color: white;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        .announcement .icon {
            font-size: 1.5em;
        }
        .announcement .text {
            flex: 1;
            font-size: 0.9em;
        }
        .announcement .date {
            font-size: 0.7em;
            opacity: 0.8;
        }

        /* API Grid */
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .api-card {
            background: white;
            border-radius: 20px;
            padding: 20px;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border: 1px solid rgba(155, 89, 182, 0.1);
        }
        .api-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(155, 89, 182, 0.15);
        }
        .api-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }
        .api-icon {
            font-size: 1.8em;
        }
        .api-name {
            font-size: 1.1em;
            font-weight: bold;
            color: #6c5ce7;
        }
        .api-status {
            margin-left: auto;
            background: #e8f5e9;
            color: #4caf50;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 0.6em;
        }
        .api-desc {
            color: #888;
            font-size: 0.75em;
            margin-bottom: 15px;
        }
        .param-input {
            margin-bottom: 12px;
        }
        .param-input label {
            display: block;
            font-size: 0.7em;
            color: #9b59b6;
            margin-bottom: 4px;
            font-weight: 600;
        }
        .param-input input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            font-size: 0.85em;
            transition: all 0.3s;
        }
        .param-input input:focus {
            outline: none;
            border-color: #9b59b6;
            box-shadow: 0 0 0 3px rgba(155, 89, 182, 0.1);
        }
        .btn-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .query-btn {
            flex: 2;
            background: linear-gradient(135deg, #9b59b6, #e91e63);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.8em;
        }
        .url-btn {
            flex: 1;
            background: linear-gradient(135deg, #6c5ce7, #a363d9);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 0.8em;
        }
        .query-btn:hover, .url-btn:hover {
            opacity: 0.9;
            transform: scale(0.98);
        }
        .result {
            margin-top: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 12px;
            max-height: 250px;
            overflow-y: auto;
            display: none;
            font-size: 0.7em;
        }
        .result.show {
            display: block;
        }
        .result pre {
            white-space: pre-wrap;
            font-family: monospace;
            color: #333;
        }
        .result-image {
            max-width: 100%;
            border-radius: 10px;
        }
        .result-audio {
            width: 100%;
        }
        .loading {
            text-align: center;
            padding: 10px;
            display: none;
            color: #9b59b6;
            font-size: 0.8em;
        }
        .loading.show {
            display: block;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            color: #9b59b6;
            font-size: 0.7em;
            border-top: 1px solid rgba(155, 89, 182, 0.2);
        }
        .footer a {
            color: #e91e63;
            text-decoration: none;
        }

        /* Gizli Admin Butonu */
        .hidden-admin {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            background: transparent;
            cursor: pointer;
            opacity: 0.15;
            z-index: 999;
        }

        /* Admin Modal */
        .admin-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .admin-modal.show {
            display: flex;
        }
        .admin-modal-content {
            background: white;
            border-radius: 20px;
            padding: 25px;
            width: 450px;
            max-width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .admin-modal-content h3 {
            color: #9b59b6;
            margin-bottom: 20px;
        }
        .admin-modal-content input, .admin-modal-content textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 12px;
            border: 1px solid #ddd;
            border-radius: 10px;
        }
        .admin-modal-content button {
            background: linear-gradient(135deg, #9b59b6, #e91e63);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            margin-right: 10px;
        }
        hr {
            margin: 15px 0;
            border: none;
            border-top: 1px solid #eee;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">KENEVİZ <span>WEB SORGULAMA</span></div>
            <div class="subtitle">⚡ SİSTEMİ v3.0 ⚡</div>
        </div>

        <div class="stats-bar">
            <div class="stat-card">
                <h3>👥 ZİYARETÇİ</h3>
                <div class="number">{{ visitor_count }}</div>
            </div>
            <div class="stat-card">
                <h3>🟢 AKTİF</h3>
                <div class="number">{{ active_count }}</div>
            </div>
            <div class="stat-card">
                <h3>📊 API</h3>
                <div class="number">{{ apis|length }}</div>
            </div>
            <div class="stat-card">
                <h3>⚡ HİZMET</h3>
                <div class="number">24/7</div>
            </div>
        </div>

        {% if announcement %}
        <div class="announcement">
            <div class="icon">📢</div>
            <div class="text">{{ announcement.text }}</div>
            <div class="date">{{ announcement.date }}</div>
        </div>
        {% endif %}

        <div class="api-grid" id="apiGrid"></div>

        <div class="footer">
            <p>⚡ KENEVİZ API • <a href="#">@KenevizOrjin</a></p>
            <p>📌 KULLANIM | Bir API seçin ve sorgulama yapın</p>
        </div>
    </div>

    <!-- Gizli Admin Butonu -->
    <div class="hidden-admin" onclick="openAdminModal()"></div>

    <!-- Admin Modal -->
    <div id="adminModal" class="admin-modal">
        <div class="admin-modal-content">
            <h3>🔐 ADMIN PANEL</h3>
            <input type="password" id="adminKey" placeholder="Admin Key">
            <button onclick="checkAdmin()">GİRİŞ</button>
            <button onclick="closeAdminModal()">KAPAT</button>
            <div id="adminPanel" style="display:none; margin-top:20px;">
                <hr>
                <h4>📢 DUYURU EKLE</h4>
                <textarea id="announceText" rows="2" placeholder="Duyuru metni..."></textarea>
                <button onclick="addAnnouncement()">📢 YAYINLA</button>
                <hr>
                <h4>➕ YENİ API EKLE</h4>
                <input type="text" id="apiName" placeholder="API Adı">
                <input type="text" id="apiEndpoint" placeholder="Endpoint URL">
                <textarea id="apiParams" rows="2" placeholder='{"param": ""}'></textarea>
                <input type="text" id="apiMethod" value="GET">
                <input type="text" id="apiType" value="json">
                <input type="text" id="apiIcon" value="🔧">
                <input type="text" id="apiDesc" placeholder="Açıklama">
                <button onclick="addApi()">➕ EKLE</button>
                <hr>
                <h4>🗑️ API SİL</h4>
                <input type="number" id="delId" placeholder="API ID">
                <button onclick="deleteApi()">🗑️ SİL</button>
            </div>
        </div>
    </div>

    <script>
        let apisData = {{ apis|tojson|safe }};
        let apiUsage = {{ api_usage|tojson|safe }};
        const ADMIN_KEY = "devkeneviz";

        function renderApis() {
            const grid = document.getElementById('apiGrid');
            grid.innerHTML = '';
            for (const [id, api] of Object.entries(apisData)) {
                let paramsHtml = '';
                for (const [pName, pVal] of Object.entries(api.params || {})) {
                    paramsHtml += `<div class="param-input">
                        <label>${pName}:</label>
                        <input type="text" data-param="${pName}" placeholder="${pVal}">
                    </div>`;
                }
                let usage = apiUsage[id] || 0;
                grid.innerHTML += `
                    <div class="api-card" data-api-id="${id}">
                        <div class="api-header">
                            <div class="api-icon">${api.icon || '🔧'}</div>
                            <div class="api-name">${api.name}</div>
                            <div class="api-status">HAZIR</div>
                        </div>
                        <div class="api-desc">${api.desc || ''}</div>
                        ${paramsHtml}
                        <div class="btn-group">
                            <button class="query-btn" onclick="queryApi(${id})">🚀 SORGULA</button>
                            <button class="url-btn" onclick="openEndpoint(${id})">🔗 URL</button>
                        </div>
                        <div class="loading" id="load-${id}">⏳ İşleniyor...</div>
                        <div class="result" id="result-${id}"></div>
                    </div>
                `;
            }
        }

        async function queryApi(apiId) {
            const card = document.querySelector(`.api-card[data-api-id="${apiId}"]`);
            const params = {};
            card.querySelectorAll('.param-input input').forEach(inp => {
                const pName = inp.getAttribute('data-param');
                if (inp.value) params[pName] = inp.value;
            });

            const loadDiv = document.getElementById(`load-${apiId}`);
            const resultDiv = document.getElementById(`result-${apiId}`);
            loadDiv.classList.add('show');
            resultDiv.classList.remove('show');

            try {
                const res = await fetch(`/api/query/${apiId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ params })
                });
                const data = await res.json();
                if (data.success) {
                    if (data.response_type === 'image') {
                        resultDiv.innerHTML = `<img src="data:${data.content_type};base64,${data.image_base64}" class="result-image">`;
                    } else if (data.response_type === 'audio') {
                        resultDiv.innerHTML = `<audio controls src="data:${data.content_type};base64,${data.audio_base64}" class="result-audio"></audio>`;
                    } else {
                        resultDiv.innerHTML = `<pre>${JSON.stringify(data.data, null, 2)}</pre>`;
                    }
                    await fetch(`/api/usage/${apiId}`, { method: 'POST' });
                } else {
                    resultDiv.innerHTML = `<pre style="color:#e91e63;">❌ HATA: ${data.error}</pre>`;
                }
                resultDiv.classList.add('show');
            } catch(e) {
                resultDiv.innerHTML = `<pre style="color:#e91e63;">❌ HATA: ${e.message}</pre>`;
                resultDiv.classList.add('show');
            } finally {
                loadDiv.classList.remove('show');
            }
        }

        function openEndpoint(apiId) {
            const api = apisData[apiId];
            if (api) window.open(api.endpoint, '_blank');
        }

        function openAdminModal() {
            document.getElementById('adminModal').classList.add('show');
            document.getElementById('adminPanel').style.display = 'none';
        }

        function closeAdminModal() {
            document.getElementById('adminModal').classList.remove('show');
        }

        function checkAdmin() {
            const key = document.getElementById('adminKey').value;
            if (key === ADMIN_KEY) {
                document.getElementById('adminPanel').style.display = 'block';
                document.getElementById('adminKey').value = '';
            } else {
                alert('❌ Hatalı Admin Key!');
            }
        }

        async function addAnnouncement() {
            const text = document.getElementById('announceText').value;
            if (!text) { alert('Duyuru metni girin!'); return; }
            const res = await fetch('/api/announcement', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            if (data.success) {
                alert('Duyuru eklendi!');
                location.reload();
            }
        }

        async function addApi() {
            let params = {};
            try { params = JSON.parse(document.getElementById('apiParams').value || '{}'); } catch(e) {}
            const res = await fetch('/api/admin/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: document.getElementById('apiName').value,
                    endpoint: document.getElementById('apiEndpoint').value,
                    params: params,
                    method: document.getElementById('apiMethod').value,
                    desc: document.getElementById('apiDesc').value,
                    response_type: document.getElementById('apiType').value,
                    icon: document.getElementById('apiIcon').value
                })
            });
            const data = await res.json();
            if (data.success) { alert('API eklendi! ID: ' + data.api_id); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }

        async function deleteApi() {
            const id = document.getElementById('delId').value;
            if (!id) { alert('ID girin!'); return; }
            const res = await fetch(`/api/admin/delete/${id}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.success) { alert('Silindi!'); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }

        renderApis();

        // Aktif kullanıcı güncelleme
        setInterval(() => {
            fetch('/api/heartbeat', { method: 'POST' });
        }, 30000);
    </script>
</body>
</html>
'''

# ============ ROUTES ============
@app.route('/')
def index():
    global VISITOR_COUNT
    session.permanent = True
    VISITOR_COUNT += 1
    
    # Aktif kullanıcıları güncelle
    session_id = request.headers.get('User-Agent', str(random.random()))
    ACTIVE_USERS[session_id] = time.time()
    
    # 5 dakikadan eski kullanıcıları temizle
    now = time.time()
    expired = [k for k, v in ACTIVE_USERS.items() if now - v > 300]
    for k in expired:
        del ACTIVE_USERS[k]
    
    current_announcement = ANNOUNCEMENTS[-1] if ANNOUNCEMENTS else None
    
    total_api_usage = sum(API_USAGE.values())
    
    return render_template_string(HTML_TEMPLATE, 
                                  apis=APIS_DB,
                                  visitor_count=VISITOR_COUNT,
                                  active_count=len(ACTIVE_USERS),
                                  announcement=current_announcement,
                                  api_usage=API_USAGE)

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    session_id = request.headers.get('User-Agent', str(random.random()))
    ACTIVE_USERS[session_id] = time.time()
    return jsonify({"success": True})

@app.route('/api/announcement', methods=['POST'])
def add_announcement():
    data = request.json
    text = data.get('text', '')
    if text:
        ANNOUNCEMENTS.append({
            'text': text,
            'date': datetime.now().strftime('%d.%m.%Y %H:%M')
        })
        if len(ANNOUNCEMENTS) > 10:
            ANNOUNCEMENTS.pop(0)
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/api/query/<int:api_id>', methods=['POST'])
def query_api(api_id):
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    
    API_USAGE[str(api_id)] = API_USAGE.get(str(api_id), 0) + 1
    
    api = APIS_DB[api_id]
    params = request.json.get('params', {})
    params = {k: v for k, v in params.items() if v}
    
    try:
        if api['method'] == 'GET':
            response = requests.get(api['endpoint'], params=params, timeout=30)
        else:
            response = requests.post(api['endpoint'], json=params, timeout=30)
        
        if api.get('response_type') == 'image' and 'image' in response.headers.get('content-type', ''):
            return jsonify({
                "success": True,
                "response_type": "image",
                "image_base64": base64.b64encode(response.content).decode(),
                "content_type": response.headers.get('content-type')
            })
        elif api.get('response_type') == 'audio' and 'audio' in response.headers.get('content-type', ''):
            return jsonify({
                "success": True,
                "response_type": "audio",
                "audio_base64": base64.b64encode(response.content).decode(),
                "content_type": response.headers.get('content-type')
            })
        else:
            try:
                result = response.json()
            except:
                result = {"raw_text": response.text[:5000]}
            return jsonify({"success": True, "response_type": "json", "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/usage/<int:api_id>', methods=['POST'])
def update_usage(api_id):
    API_USAGE[str(api_id)] = API_USAGE.get(str(api_id), 0) + 1
    return jsonify({"success": True})

@app.route('/api/admin/add', methods=['POST'])
def add_api():
    data = request.json
    if not data.get('endpoint'):
        return jsonify({"error": "Endpoint gerekli"}), 400
    
    new_id = generate_api_id()
    APIS_DB[new_id] = {
        "name": data.get('name', 'Yeni API'),
        "endpoint": data['endpoint'],
        "params": data.get('params', {}),
        "method": data.get('method', 'GET'),
        "desc": data.get('desc', ''),
        "response_type": data.get('response_type', 'json'),
        "icon": data.get('icon', '🔧')
    }
    return jsonify({"success": True, "api_id": new_id})

@app.route('/api/admin/delete/<int:api_id>', methods=['DELETE'])
def delete_api(api_id):
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    del APIS_DB[api_id]
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(port=8080)
