from flask import Flask, request, jsonify, render_template_string, session
import requests
import base64
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "keneviz_secret_key_2026"

ADMIN_KEY = "devkeneviz"

# Veritabanları
APIS_DB = {
    1001: {
        "name": "Görsel Üret",
        "endpoint": "https://kenevizimagegenerate.vercel.app/api/generate",
        "params": {"prompt": ""},
        "method": "GET",
        "desc": "Yapay zeka ile görsel oluştur",
        "response_type": "image"
    },
    1002: {
        "name": "Ses Sentez",
        "endpoint": "https://kenevizttsapi.vercel.app/api/tts",
        "params": {"text": "", "lang": "tr"},
        "method": "GET",
        "desc": "Metni sese dönüştür",
        "response_type": "audio"
    },
    1003: {
        "name": "GSM İsim Sorgu",
        "endpoint": "https://kenevizglobalgsm-nameapi.vercel.app/api/gsm-name",
        "params": {"number": ""},
        "method": "GET",
        "desc": "Telefon numarası sahibini sorgula",
        "response_type": "json"
    },
    1004: {
        "name": "Tabii Checker",
        "endpoint": "https://keneviztabiicheckerapi.vercel.app/tabiicheck",
        "params": {"login": ""},
        "method": "GET",
        "desc": "Hesap doğrulama kontrolü",
        "response_type": "json"
    },
    1005: {
        "name": "Ayak Sorgu",
        "endpoint": "https://kenevizayaksorguapi.vercel.app/api/sorgula",
        "params": {"tgnick": "", "yas": ""},
        "method": "GET",
        "desc": "Kullanıcı bilgisi sorgula",
        "response_type": "json"
    },
    1006: {
        "name": "URL IP Çek",
        "endpoint": "https://kenevizurlipcekiciapi.vercel.app/urlipcek",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Domain IP adresini bul",
        "response_type": "json"
    },
    1007: {
        "name": "BIN Sorgu",
        "endpoint": "https://kenevizbinsorguapi.vercel.app/binsorgu",
        "params": {"bin": ""},
        "method": "GET",
        "desc": "Kart BIN sorgulama",
        "response_type": "json"
    },
    1008: {
        "name": "Index Çek",
        "endpoint": "https://kenevizindexcekenapi.vercel.app/index",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Site kaynak kodunu al",
        "response_type": "text"
    },
    1009: {
        "name": "Web MS Analiz",
        "endpoint": "https://kenevizwebmsapi.vercel.app/analyze",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Web sitesi performans analizi",
        "response_type": "json"
    }
}

MESSAGES = []
VISITOR_COUNT = 0
API_USAGE = {}

def generate_api_id():
    new_id = random.randint(1000, 9999)
    while new_id in APIS_DB:
        new_id = random.randint(1000, 9999)
    return new_id

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔮 KENEVIZ API PORTAL</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
            margin-bottom: 30px;
            padding: 20px;
        }
        .header h1 {
            font-size: 2.2em;
            background: linear-gradient(135deg, #6c5ce7, #a363d9, #e84393);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .dev-tag {
            color: #6c5ce7;
            font-size: 0.8em;
            margin-top: 8px;
            opacity: 0.7;
        }
        
        /* Stats */
        .stats {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 12px 24px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .stat-card h3 {
            color: #6c5ce7;
            font-size: 0.7em;
            margin-bottom: 5px;
        }
        .stat-card .number {
            color: #e84393;
            font-size: 1.8em;
            font-weight: bold;
        }
        
        /* Auth Section */
        .auth-section {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .auth-section h3 {
            color: #6c5ce7;
            margin-bottom: 15px;
        }
        .auth-input {
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 25px;
            width: 250px;
            margin-right: 10px;
        }
        .auth-btn {
            background: linear-gradient(135deg, #6c5ce7, #a363d9);
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 25px;
            cursor: pointer;
        }
        .user-badge {
            display: inline-block;
            background: #6c5ce7;
            color: white;
            padding: 5px 15px;
            border-radius: 25px;
        }
        
        /* Support Section (sadece admin görür) */
        .support-section {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            display: {{ 'block' if session.get('admin') else 'none' }};
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .support-section h3 {
            color: #6c5ce7;
            margin-bottom: 15px;
        }
        .support-section input, .support-section textarea {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-family: inherit;
        }
        .message-item {
            background: #f8f9fa;
            border-left: 3px solid #6c5ce7;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 8px;
        }
        .message-name {
            color: #6c5ce7;
            font-weight: bold;
        }
        .message-text {
            color: #333;
            margin-top: 5px;
        }
        .message-date {
            color: #999;
            font-size: 0.7em;
            margin-top: 5px;
        }
        
        /* Admin Panel (gizli) */
        .admin-content {
            display: none;
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .admin-content.show {
            display: block;
        }
        
        /* API Grid */
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .api-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s;
        }
        .api-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .api-card h3 {
            color: #6c5ce7;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        .api-id {
            background: #e0eafc;
            color: #6c5ce7;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 0.7em;
            margin-left: 8px;
        }
        .api-endpoint {
            color: #888;
            font-size: 0.65em;
            word-break: break-all;
            background: #f8f9fa;
            padding: 6px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .api-desc {
            color: #555;
            font-size: 0.75em;
            margin-bottom: 15px;
        }
        .api-stats {
            color: #aaa;
            font-size: 0.65em;
            margin-bottom: 10px;
        }
        
        .param-input {
            margin-bottom: 12px;
        }
        .param-input label {
            display: block;
            font-size: 0.7em;
            color: #6c5ce7;
            margin-bottom: 4px;
            font-weight: 500;
        }
        .param-input input {
            width: 100%;
            padding: 10px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            font-family: inherit;
        }
        .param-input input:focus {
            outline: none;
            border-color: #6c5ce7;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .query-btn {
            flex: 2;
            background: linear-gradient(135deg, #6c5ce7, #a363d9);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
        }
        .url-btn {
            flex: 1;
            background: linear-gradient(135deg, #00b894, #00cec9);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 25px;
            cursor: pointer;
        }
        .query-btn:hover, .url-btn:hover {
            opacity: 0.9;
        }
        
        .result {
            margin-top: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 10px;
            max-height: 250px;
            overflow-y: auto;
            display: none;
        }
        .result.show {
            display: block;
        }
        .result pre {
            color: #333;
            font-size: 0.7em;
            white-space: pre-wrap;
            font-family: monospace;
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
            color: #6c5ce7;
        }
        .loading.show {
            display: block;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #888;
            font-size: 0.7em;
            border-top: 1px solid #e0e0e0;
        }
        
        /* Gizli Admin Butonu (sağ alt köşe) */
        .hidden-admin-btn {
            position: fixed;
            bottom: 15px;
            right: 15px;
            width: 30px;
            height: 30px;
            background: transparent;
            cursor: pointer;
            z-index: 999;
            opacity: 0.2;
        }
        
        /* Admin Modal */
        .admin-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.4);
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
            width: 400px;
            max-width: 90%;
        }
        .admin-modal-content h3 {
            color: #6c5ce7;
            margin-bottom: 15px;
        }
        .admin-modal-content input {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 10px;
        }
        .admin-modal-content button {
            background: #6c5ce7;
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
        
        input, textarea {
            font-family: inherit;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #6c5ce7;
            font-weight: 500;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔮 KENEVIZ API PORTAL</h1>
            <div class="dev-tag">DEV : KENEViZ</div>
        </div>
        
        <div class="stats">
            <div class="stat-card"><h3>👥 ZİYARETÇİ</h3><div class="number">{{ visitor_count }}</div></div>
            <div class="stat-card"><h3>📊 API KULLANIM</h3><div class="number">{{ total_api_usage }}</div></div>
            <div class="stat-card"><h3>🔐 DURUM</h3><div class="number">{{ 'ADMIN' if session.get('admin') else 'MİSAFİR' }}</div></div>
        </div>
        
        <!-- Auth Section (sadece normal kullanıcılar için) -->
        <div class="auth-section" id="authSection">
            <h3>🔐 HOŞ GELDİNİZ</h3>
            {% if session.get('admin') %}
                <div class="user-badge">✅ Admin olarak giriş yaptınız</div>
                <button class="auth-btn" onclick="logout()" style="margin-left: 10px;">🚪 ÇIKIŞ</button>
            {% else %}
                <p style="color:#888;">API'leri kullanmak için misafir olarak devam edin</p>
                <button class="auth-btn" onclick="guestLogin()">👤 MİSAFİR GİRİŞİ</button>
            {% endif %}
        </div>
        
        <!-- Admin Mesajları (sadece admin görür) -->
        <div class="support-section" id="supportSection">
            <h3>💬 KULLANICI MESAJLARI</h3>
            <div id="messagesList" style="max-height: 300px; overflow-y: auto;">
                {% for msg in messages %}
                <div class="message-item">
                    <div class="message-name">{{ msg.name }}</div>
                    <div class="message-text">{{ msg.text }}</div>
                    <div class="message-date">{{ msg.date }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Gizli Admin Panel İçeriği (modal ile) -->
        <div id="adminModal" class="admin-modal">
            <div class="admin-modal-content">
                <h3>🔐 ADMIN PANEL</h3>
                <input type="password" id="adminKeyInput" placeholder="Admin Key">
                <button onclick="checkAdminLogin()">GİRİŞ</button>
                <button onclick="closeAdminModal()">KAPAT</button>
                <div id="adminTools" style="display:none; margin-top:20px;">
                    <hr><h4>➕ YENİ API EKLE</h4>
                    <input type="text" id="newApiName" placeholder="API Adı">
                    <input type="text" id="newApiEndpoint" placeholder="Endpoint URL">
                    <textarea id="newApiParams" rows="2" placeholder='{"param": ""}'></textarea>
                    <input type="text" id="newApiMethod" value="GET">
                    <input type="text" id="newApiResponseType" value="json">
                    <input type="text" id="newApiDesc" placeholder="Açıklama">
                    <button onclick="addApi()">➕ EKLE</button>
                    <hr><h4>🗑️ API SİL</h4>
                    <input type="number" id="deleteApiId" placeholder="API ID">
                    <button onclick="deleteApi()">🗑️ SİL</button>
                    <hr><h4>📊 TÜM API'LER</h4>
                    <button onclick="listApis()">📋 LİSTELE</button>
                    <pre id="apiListResult" style="margin-top:10px; background:#f8f9fa; padding:10px; border-radius:8px; font-size:10px; display:none;"></pre>
                </div>
            </div>
        </div>
        
        <!-- Gizli Admin Butonu -->
        <div class="hidden-admin-btn" onclick="openAdminModal()" title="Admin"></div>
        
        <div class="api-grid" id="apiGrid"></div>
        
        <div class="footer">
            <p>🔥 KENEVIZ API PORTAL | v3.0 🔥</p>
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
                let usageCount = apiUsage[id] || 0;
                grid.innerHTML += `
                    <div class="api-card" data-api-id="${id}">
                        <h3>${api.name} <span class="api-id">ID:${id}</span></h3>
                        <div class="api-endpoint">📡 ${api.endpoint}</div>
                        <div class="api-desc">${api.desc || ''}</div>
                        <div class="api-stats">📊 Kullanım: ${usageCount} kez</div>
                        ${paramsHtml}
                        <div class="button-group">
                            <button class="query-btn" onclick="queryApi(${id})">🚀 SORGULA</button>
                            <button class="url-btn" onclick="openEndpoint(${id})">🔗 URL'DE AÇ</button>
                        </div>
                        <div class="loading" id="loading-${id}">⏳ İşleniyor...</div>
                        <div class="result" id="result-${id}"></div>
                    </div>
                `;
            }
        }
        
        async function queryApi(apiId) {
            const card = document.querySelector(`[data-api-id="${apiId}"]`);
            const params = {};
            card.querySelectorAll('.param-input input').forEach(inp => {
                const pName = inp.getAttribute('data-param');
                if (inp.value && pName) params[pName] = inp.value;
            });
            
            const loadingDiv = document.getElementById(`loading-${apiId}`);
            const resultDiv = document.getElementById(`result-${apiId}`);
            loadingDiv.classList.add('show');
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
                        resultDiv.innerHTML = `<audio controls class="result-audio" src="data:${data.content_type};base64,${data.audio_base64}"></audio>`;
                    } else {
                        resultDiv.innerHTML = `<pre>${JSON.stringify(data.data, null, 2)}</pre>`;
                    }
                    await fetch(`/api/usage/${apiId}`, { method: 'POST' });
                    location.reload();
                } else {
                    resultDiv.innerHTML = `<pre style="color:#e84393;">❌ HATA: ${data.error}</pre>`;
                }
                resultDiv.classList.add('show');
            } catch(e) {
                resultDiv.innerHTML = `<pre style="color:#e84393;">❌ BAĞLANTI HATASI: ${e.message}</pre>`;
                resultDiv.classList.add('show');
            } finally {
                loadingDiv.classList.remove('show');
            }
        }
        
        function openEndpoint(apiId) {
            const api = apisData[apiId];
            if (api) window.open(api.endpoint, '_blank');
        }
        
        function guestLogin() {
            fetch('/api/guest', { method: 'POST' }).then(() => location.reload());
        }
        
        function logout() {
            fetch('/api/logout', { method: 'POST' }).then(() => location.reload());
        }
        
        function openAdminModal() {
            document.getElementById('adminModal').classList.add('show');
            document.getElementById('adminTools').style.display = 'none';
            document.getElementById('adminKeyInput').value = '';
        }
        
        function closeAdminModal() {
            document.getElementById('adminModal').classList.remove('show');
        }
        
        function checkAdminLogin() {
            const key = document.getElementById('adminKeyInput').value;
            if (key === ADMIN_KEY) {
                fetch('/api/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: key })
                }).then(() => {
                    location.reload();
                });
            } else {
                alert('❌ Hatalı Admin Key!');
            }
        }
        
        async function addApi() {
            const key = ADMIN_KEY;
            let params = {};
            try { params = JSON.parse(document.getElementById('newApiParams').value || '{}'); } catch(e) {}
            const res = await fetch('/api/admin/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Admin-Key': key },
                body: JSON.stringify({
                    name: document.getElementById('newApiName').value,
                    endpoint: document.getElementById('newApiEndpoint').value,
                    params: params,
                    method: document.getElementById('newApiMethod').value,
                    desc: document.getElementById('newApiDesc').value,
                    response_type: document.getElementById('newApiResponseType').value
                })
            });
            const data = await res.json();
            if (data.success) { alert('API eklendi! ID: ' + data.api_id); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        async function deleteApi() {
            const key = ADMIN_KEY;
            const id = document.getElementById('deleteApiId').value;
            if (!id) { alert('ID girin'); return; }
            const res = await fetch(`/api/admin/delete/${id}`, { method: 'DELETE', headers: { 'X-Admin-Key': key } });
            const data = await res.json();
            if (data.success) { alert('Silindi!'); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        async function listApis() {
            const key = ADMIN_KEY;
            const res = await fetch('/api/admin/list?admin_key=' + key);
            const data = await res.json();
            const resultDiv = document.getElementById('apiListResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = JSON.stringify(data, null, 2);
        }
        
        renderApis();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    global VISITOR_COUNT
    VISITOR_COUNT += 1
    total_api = sum(API_USAGE.values())
    return render_template_string(HTML_TEMPLATE, 
                                  apis=APIS_DB, 
                                  visitor_count=VISITOR_COUNT,
                                  total_api_usage=total_api,
                                  messages=MESSAGES,
                                  api_usage=API_USAGE)

@app.route('/api/guest', methods=['POST'])
def guest_login():
    session['admin'] = False
    return jsonify({"success": True})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('key') == ADMIN_KEY:
        session['admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

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
    admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Yetkisiz erişim!"}), 401
    
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
        "response_type": data.get('response_type', 'json')
    }
    return jsonify({"success": True, "api_id": new_id})

@app.route('/api/admin/delete/<int:api_id>', methods=['DELETE'])
def delete_api(api_id):
    admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Yetkisiz erişim!"}), 401
    
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    
    del APIS_DB[api_id]
    return jsonify({"success": True})

@app.route('/api/admin/list', methods=['GET'])
def list_apis():
    admin_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Yetkisiz erişim!"}), 401
    return jsonify(APIS_DB)

if __name__ == '__main__':
    app.run(port=8080)
