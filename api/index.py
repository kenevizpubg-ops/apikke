from flask import Flask, request, jsonify, render_template_string
import requests
import json
import base64
import random

app = Flask(__name__)

# ============ ADMIN KEY ============
ADMIN_KEY = "devkeneviz"

# ============ API VERİTABANI ============
APIS_DB = {
    1001: {
        "name": "Görsel Üret",
        "endpoint": "https://kenevizimagegenerate.vercel.app/api/generate",
        "params": {"prompt": ""},
        "method": "GET",
        "desc": "AI ile görsel oluşturur",
        "response_type": "image"
    },
    1002: {
        "name": "Ses Sentez",
        "endpoint": "https://kenevizttsapi.vercel.app/api/tts",
        "params": {"text": "", "lang": "tr"},
        "method": "GET",
        "desc": "Metni sese çevirir",
        "response_type": "audio"
    },
    1003: {
        "name": "GSM İsim Sorgu",
        "endpoint": "https://kenevizglobalgsm-nameapi.vercel.app/api/gsm-name",
        "params": {"number": ""},
        "method": "GET",
        "desc": "Numara sahibini sorgular",
        "response_type": "json"
    },
    1004: {
        "name": "Tabii Checker",
        "endpoint": "https://keneviztabiicheckerapi.vercel.app/tabiicheck",
        "params": {"login": ""},
        "method": "GET",
        "desc": "Hesap doğrulama",
        "response_type": "json"
    },
    1005: {
        "name": "Ayak Sorgu",
        "endpoint": "https://kenevizayaksorguapi.vercel.app/api/sorgula",
        "params": {"tgnick": "", "yas": ""},
        "method": "GET",
        "desc": "Kullanıcı bilgisi sorgular",
        "response_type": "json"
    },
    1006: {
        "name": "URL IP Çek",
        "endpoint": "https://kenevizurlipcekiciapi.vercel.app/urlipcek",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Domain'in IP adresini bulur",
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
        "desc": "Site kaynak kodunu alır",
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

def generate_api_id():
    new_id = random.randint(1000, 9999)
    while new_id in APIS_DB:
        new_id = random.randint(1000, 9999)
    return new_id

# ============ HTML ŞABLONU ============
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
            background: linear-gradient(135deg, #f5f0ff 0%, #fce4ec 50%, #e8eaf6 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; }
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #9b59b6, #e91e63, #2196f3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hidden-admin {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            background: transparent;
            cursor: pointer;
            opacity: 0.2;
        }
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
        .admin-modal.show { display: flex; }
        .admin-modal-content {
            background: white;
            border-radius: 20px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .admin-modal-content input, .admin-modal-content textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
        }
        .admin-modal-content button {
            background: linear-gradient(135deg, #9b59b6, #e91e63);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
        }
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 25px;
        }
        .api-card {
            background: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .api-card:hover { transform: translateY(-5px); }
        .api-card h3 { color: #9b59b6; margin-bottom: 10px; }
        .api-id {
            background: #e8eaf6;
            color: #5e35b1;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.7em;
        }
        .api-endpoint {
            background: #f5f0ff;
            padding: 8px;
            border-radius: 10px;
            font-size: 0.7em;
            word-break: break-all;
            margin-bottom: 10px;
        }
        .param-input { margin-bottom: 10px; }
        .param-input label { display: block; font-size: 0.75em; color: #7b1fa2; }
        .param-input input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 10px;
        }
        .button-group { display: flex; gap: 10px; margin-top: 15px; }
        .query-btn {
            flex: 2;
            background: linear-gradient(135deg, #9b59b6, #e91e63);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 30px;
            cursor: pointer;
        }
        .url-btn {
            flex: 1;
            background: linear-gradient(135deg, #2196f3, #00bcd4);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 30px;
            cursor: pointer;
        }
        .result {
            margin-top: 15px;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 10px;
            max-height: 200px;
            overflow-y: auto;
            display: none;
        }
        .result.show { display: block; }
        .result pre { font-size: 0.7em; white-space: pre-wrap; }
        .result-image { max-width: 100%; border-radius: 10px; }
        .result-audio { width: 100%; }
        .loading {
            text-align: center;
            padding: 10px;
            display: none;
            color: #9b59b6;
        }
        .loading.show { display: block; }
        .footer { text-align: center; margin-top: 40px; color: #9b59b6; font-size: 0.7em; }
        hr { margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔮 KENEVIZ API PORTAL</h1>
            <p>Gelişmiş API Sorgulama Sistemi</p>
        </div>
        <div class="api-grid" id="apiGrid"></div>
        <div class="footer">
            <p>🔥 KENEVIZ API PORTAL | v2.0 🔥</p>
        </div>
    </div>
    
    <div class="hidden-admin" onclick="openAdminModal()"></div>
    
    <div id="adminModal" class="admin-modal">
        <div class="admin-modal-content">
            <h3>🔐 ADMIN PANEL</h3>
            <input type="password" id="adminKeyInput" placeholder="Admin Key">
            <button onclick="checkAdminKey()">Giriş</button>
            <button onclick="closeAdminModal()">Kapat</button>
            <div id="adminTools" style="display:none; margin-top:20px;">
                <hr><h3>➕ Yeni API Ekle</h3>
                <input type="text" id="newApiName" placeholder="API Adı">
                <input type="text" id="newApiEndpoint" placeholder="Endpoint URL">
                <textarea id="newApiParams" rows="2" placeholder='{"param":""}'></textarea>
                <input type="text" id="newApiMethod" value="GET">
                <input type="text" id="newApiResponseType" value="json">
                <input type="text" id="newApiDesc" placeholder="Açıklama">
                <button onclick="addApi()">➕ Ekle</button>
                <hr><h3>🗑️ API Sil</h3>
                <input type="number" id="deleteApiId" placeholder="API ID">
                <button onclick="deleteApi()">🗑️ Sil</button>
            </div>
        </div>
    </div>
    
    <script>
        let apisData = {{ apis|tojson|safe }};
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
                grid.innerHTML += `
                    <div class="api-card" data-api-id="${id}">
                        <h3>${api.name} <span class="api-id">ID:${id}</span></h3>
                        <div class="api-endpoint">📡 ${api.endpoint}</div>
                        <div class="api-desc">${api.desc || ''}</div>
                        ${paramsHtml}
                        <div class="button-group">
                            <button class="query-btn" onclick="queryApi(${id})">🚀 Sorgula</button>
                            <button class="url-btn" onclick="openEndpoint(${id})">🔗 URL'de Aç</button>
                        </div>
                        <div class="loading" id="loading-${id}">⏳ İşleniyor...</div>
                        <div class="result" id="result-${id}"></div>
                    </div>
                `;
            }
        }
        
        function openAdminModal() { document.getElementById('adminModal').classList.add('show'); }
        function closeAdminModal() { document.getElementById('adminModal').classList.remove('show'); }
        
        function checkAdminKey() {
            const key = document.getElementById('adminKeyInput').value;
            if (key === ADMIN_KEY) {
                document.getElementById('adminTools').style.display = 'block';
            } else { alert('Hatalı key!'); }
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
                        resultDiv.innerHTML = `<audio controls src="data:${data.content_type};base64,${data.audio_base64}"></audio>`;
                    } else {
                        resultDiv.innerHTML = `<pre>${JSON.stringify(data.data, null, 2)}</pre>`;
                    }
                } else {
                    resultDiv.innerHTML = `<pre style="color:red;">❌ ${data.error}</pre>`;
                }
                resultDiv.classList.add('show');
            } catch(e) {
                resultDiv.innerHTML = `<pre style="color:red;">❌ Hata: ${e.message}</pre>`;
                resultDiv.classList.add('show');
            } finally {
                loadingDiv.classList.remove('show');
            }
        }
        
        function openEndpoint(apiId) {
            const api = apisData[apiId];
            if (api) window.open(api.endpoint, '_blank');
        }
        
        async function addApi() {
            const key = document.getElementById('adminKeyInput').value;
            if (key !== ADMIN_KEY) { alert('Admin key hatalı'); return; }
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
            const key = document.getElementById('adminKeyInput').value;
            if (key !== ADMIN_KEY) { alert('Admin key hatalı'); return; }
            const id = document.getElementById('deleteApiId').value;
            if (!id) { alert('ID girin'); return; }
            const res = await fetch(`/api/admin/delete/${id}`, { method: 'DELETE', headers: { 'X-Admin-Key': key } });
            const data = await res.json();
            if (data.success) { alert('Silindi!'); location.reload(); }
            else { alert('Hata: ' + data.error); }
        }
        
        renderApis();
    </script>
</body>
</html>
'''

# ============ ROUTES ============
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, apis=APIS_DB)

@app.route('/api/query/<int:api_id>', methods=['POST'])
def query_api(api_id):
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    
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

# Vercel için
app.debug = False