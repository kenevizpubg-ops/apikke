from flask import Flask, request, jsonify, render_template_string, session
import requests
import base64
import random
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "keneviz_secret_key_2026"

ADMIN_KEY = "devkeneviz"

# ============ TÜM API'LER ============
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
    },
    10: {
        "name": "GSM SORGU",
        "endpoint": "https://kenevizglobalgsm-nameapi.vercel.app/api/gsm-name",
        "params": {"number": ""},
        "method": "GET",
        "desc": "Telefon numarası sahibini sorgula",
        "response_type": "json",
        "icon": "📱"
    },
    11: {
        "name": "TABİİ CHECKER",
        "endpoint": "https://keneviztabiicheckerapi.vercel.app/tabiicheck",
        "params": {"login": ""},
        "method": "GET",
        "desc": "Hesap doğrulama kontrolü",
        "response_type": "json",
        "icon": "✅"
    },
    12: {
        "name": "URL IP ÇEK",
        "endpoint": "https://kenevizurlipcekiciapi.vercel.app/urlipcek",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Domain IP adresini bul",
        "response_type": "json",
        "icon": "🌐"
    },
    13: {
        "name": "BİN SORGU",
        "endpoint": "https://kenevizbinsorguapi.vercel.app/binsorgu",
        "params": {"bin": ""},
        "method": "GET",
        "desc": "Kart BIN sorgulama",
        "response_type": "json",
        "icon": "💳"
    },
    14: {
        "name": "İNDEX ÇEK",
        "endpoint": "https://kenevizindexcekenapi.vercel.app/index",
        "params": {"url": ""},
        "method": "GET",
        "desc": "Site kaynak kodunu al",
        "response_type": "text",
        "icon": "📄"
    }
}

VISITOR_COUNT = 0
ACTIVE_USERS = {}
ANNOUNCEMENTS = []
API_USAGE = {}

def generate_api_id():
    new_id = random.randint(15, 999)
    while new_id in APIS_DB:
        new_id = random.randint(15, 999)
    return new_id

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KENEVİZ API PORTAL</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        /* Tema Değişkenleri */
        :root {
            --bg: linear-gradient(135deg, #f5f0ff 0%, #fce4ec 50%, #e8eaf6 100%);
            --card-bg: white;
            --text: #333;
            --text-light: #888;
            --border: rgba(155, 89, 182, 0.1);
            --shadow: rgba(0,0,0,0.05);
            --neon: 0 0 5px rgba(155, 89, 182, 0.3);
        }
        body.dark {
            --bg: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            --card-bg: #1e1e2e;
            --text: #eee;
            --text-light: #aaa;
            --border: rgba(155, 89, 182, 0.2);
            --shadow: rgba(0,0,0,0.2);
            --neon: 0 0 10px rgba(155, 89, 182, 0.5);
        }

        body {
            background: var(--bg);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            min-height: 100vh;
            padding: 20px;
            transition: all 0.3s ease;
            color: var(--text);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 30px;
            position: relative;
        }
        .logo {
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(135deg, #9b59b6, #e91e63, #6c5ce7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
            text-shadow: var(--neon);
        }
        .dev-tag {
            position: absolute;
            top: 10px;
            right: 20px;
            background: rgba(155, 89, 182, 0.15);
            padding: 5px 15px;
            border-radius: 30px;
            font-size: 0.7em;
            color: #9b59b6;
            font-weight: bold;
        }
        .subtitle {
            color: var(--text-light);
            margin-top: 10px;
            font-size: 0.9em;
        }

        /* Tema Butonu */
        .theme-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: var(--card-bg);
            border: 1px solid #9b59b6;
            border-radius: 30px;
            padding: 8px 15px;
            cursor: pointer;
            z-index: 998;
            font-size: 0.8em;
            color: var(--text);
            box-shadow: var(--shadow);
        }
        .theme-btn:hover {
            box-shadow: var(--neon);
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
            background: var(--card-bg);
            border-radius: 20px;
            padding: 15px 30px;
            text-align: center;
            box-shadow: 0 5px 15px var(--shadow);
            border: 1px solid var(--border);
        }
        .stat-card h3 {
            color: #e91e63;
            font-size: 0.75em;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .stat-card .number {
            font-size: 2.2em;
            font-weight: bold;
            color: #6c5ce7;
        }

        /* Duyuru */
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
            box-shadow: var(--neon);
        }
        .announcement .icon { font-size: 1.5em; }
        .announcement .text { flex: 1; font-size: 0.95em; }
        .announcement .date { font-size: 0.7em; opacity: 0.8; }

        /* API Grid */
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        .api-card {
            background: var(--card-bg);
            border-radius: 20px;
            padding: 20px;
            transition: all 0.3s;
            box-shadow: 0 5px 15px var(--shadow);
            border: 1px solid var(--border);
        }
        .api-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--neon);
        }
        .api-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        .api-icon { font-size: 2em; }
        .api-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #6c5ce7;
        }
        .api-status {
            margin-left: auto;
            background: #e8f5e9;
            color: #4caf50;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.65em;
        }
        .api-desc {
            color: var(--text-light);
            font-size: 0.85em;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        .param-input {
            margin-bottom: 12px;
        }
        .param-input label {
            display: block;
            font-size: 0.75em;
            color: #9b59b6;
            margin-bottom: 5px;
            font-weight: 600;
        }
        .param-input input {
            width: 100%;
            padding: 10px 14px;
            background: var(--card-bg);
            border: 1px solid #ddd;
            border-radius: 12px;
            font-size: 0.9em;
            color: var(--text);
            transition: all 0.3s;
        }
        .param-input input:focus {
            outline: none;
            border-color: #9b59b6;
            box-shadow: 0 0 0 3px rgba(155, 89, 182, 0.2);
        }
        .btn-group {
            display: flex;
            gap: 12px;
            margin-top: 15px;
        }
        .query-btn {
            flex: 2;
            background: linear-gradient(135deg, #9b59b6, #e91e63);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85em;
        }
        .url-btn {
            flex: 1;
            background: linear-gradient(135deg, #6c5ce7, #a363d9);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 0.85em;
        }
        .query-btn:hover, .url-btn:hover {
            opacity: 0.9;
            transform: scale(0.98);
        }
        .result {
            margin-top: 15px;
            padding: 12px;
            background: rgba(0,0,0,0.05);
            border-radius: 12px;
            max-height: 300px;
            overflow-y: auto;
            display: none;
            font-size: 0.8em;
        }
        .result.show { display: block; }
        .result pre {
            white-space: pre-wrap;
            font-family: monospace;
            color: var(--text);
            font-size: 0.75em;
        }
        .result-image {
            max-width: 100%;
            border-radius: 10px;
        }
        .result-audio { width: 100%; }
        .loading {
            text-align: center;
            padding: 10px;
            display: none;
            color: #9b59b6;
            font-size: 0.85em;
        }
        .loading.show { display: block; }

        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            color: var(--text-light);
            font-size: 0.75em;
            border-top: 1px solid var(--border);
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
            background: rgba(0,0,0,0.6);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .admin-modal.show { display: flex; }
        .admin-modal-content {
            background: var(--card-bg);
            border-radius: 20px;
            padding: 25px;
            width: 500px;
            max-width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid #9b59b6;
        }
        .admin-modal-content h3, .admin-modal-content h4 {
            color: #9b59b6;
            margin-bottom: 15px;
        }
        .admin-modal-content input, .admin-modal-content textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 12px;
            background: var(--card-bg);
            border: 1px solid #ddd;
            border-radius: 10px;
            color: var(--text);
        }
        .admin-modal-content button {
            background: linear-gradient(135deg, #9b59b6, #e91e63);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .announcement-item {
            background: rgba(155, 89, 182, 0.1);
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .announcement-item .text { flex: 1; font-size: 0.85em; }
        .announcement-item button {
            background: #6c5ce7;
            padding: 5px 10px;
            font-size: 0.7em;
        }
        hr { margin: 15px 0; border-color: var(--border); }
    </style>
</head>
<body>
    <button class="theme-btn" onclick="toggleTheme()">🌓 TEMA DEĞİŞTİR</button>

    <div class="container">
        <div class="header">
            <div class="logo">KENEVİZ API PORTAL</div>
            <div class="subtitle">⚡ GELİŞMİŞ API SORGULAMA SİSTEMİ ⚡</div>
            <div class="dev-tag">DEV : KENEViZ</div>
        </div>

        <div class="stats-bar">
            <div class="stat-card"><h3>👥 ZİYARETÇİ</h3><div class="number">{{ visitor_count }}</div></div>
            <div class="stat-card"><h3>🟢 AKTİF</h3><div class="number">{{ active_count }}</div></div>
            <div class="stat-card"><h3>📊 API</h3><div class="number">{{ apis|length }}</div></div>
            <div class="stat-card"><h3>⚡ HİZMET</h3><div class="number">24/7</div></div>
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
            <p>⚡ KENEVIZ API PORTAL • <a href="#">@KenevizOrjin</a></p>
            <p>📌 14+ API | 7/24 HİZMET | GÜVENLİ SORGULAMA</p>
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
                <h4>📢 DUYURU YÖNETİMİ</h4>
                <textarea id="announceText" rows="2" placeholder="Yeni duyuru metni..."></textarea>
                <button onclick="addAnnouncement()">➕ YENİ DUYURU EKLE</button>
                <div id="announceList" style="margin-top:15px;"></div>
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
        let announcements = {{ announcements|tojson|safe }};
        const ADMIN_KEY = "devkeneviz";

        // Tema değiştirme
        function toggleTheme() {
            document.body.classList.toggle('dark');
            localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
        }
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark');
        }

        // API'leri render et
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

        // Admin fonksiyonları
        function openAdminModal() {
            document.getElementById('adminModal').classList.add('show');
            document.getElementById('adminPanel').style.display = 'none';
            renderAnnouncements();
        }

        function closeAdminModal() {
            document.getElementById('adminModal').classList.remove('show');
        }

        function checkAdmin() {
            const key = document.getElementById('adminKey').value;
            if (key === ADMIN_KEY) {
                document.getElementById('adminPanel').style.display = 'block';
                document.getElementById('adminKey').value = '';
                renderAnnouncements();
            } else {
                alert('❌ Hatalı Admin Key!');
            }
        }

        function renderAnnouncements() {
            const list = document.getElementById('announceList');
            if (!list) return;
            list.innerHTML = '<h5>Mevcut Duyurular:</h5>';
            announcements.forEach((ann, idx) => {
                list.innerHTML += `
                    <div class="announcement-item">
                        <div class="text">${ann.text}</div>
                        <div class="date">${ann.date}</div>
                        <button onclick="editAnnouncement(${idx})">✏️ Düzenle</button>
                        <button onclick="deleteAnnouncement(${idx})">🗑️ Sil</button>
                        <button onclick="moveAnnouncement(${idx}, 'up')">⬆️</button>
                        <button onclick="moveAnnouncement(${idx}, 'down')">⬇️</button>
                    </div>
                `;
            });
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

        async function editAnnouncement(idx) {
            const newText = prompt('Yeni duyuru metni:', announcements[idx].text);
            if (newText) {
                const res = await fetch(`/api/announcement/${idx}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: newText })
                });
                if (res.ok) location.reload();
            }
        }

        async function deleteAnnouncement(idx) {
            if (confirm('Duyuru silinsin mi?')) {
                await fetch(`/api/announcement/${idx}`, { method: 'DELETE' });
                location.reload();
            }
        }

        async function moveAnnouncement(idx, direction) {
            await fetch(`/api/announcement/move/${idx}?direction=${direction}`, { method: 'POST' });
            location.reload();
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
    VISITOR_COUNT += 1
    
    session_id = request.headers.get('User-Agent', str(random.random()))
    ACTIVE_USERS[session_id] = time.time()
    
    now = time.time()
    expired = [k for k, v in ACTIVE_USERS.items() if now - v > 300]
    for k in expired:
        del ACTIVE_USERS[k]
    
    current_announcement = ANNOUNCEMENTS[-1] if ANNOUNCEMENTS else None
    
    return render_template_string(HTML_TEMPLATE, 
                                  apis=APIS_DB,
                                  visitor_count=VISITOR_COUNT,
                                  active_count=len(ACTIVE_USERS),
                                  announcement=current_announcement,
                                  announcements=ANNOUNCEMENTS,
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
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/api/announcement/<int:idx>', methods=['PUT'])
def edit_announcement(idx):
    if 0 <= idx < len(ANNOUNCEMENTS):
        data = request.json
        ANNOUNCEMENTS[idx]['text'] = data.get('text', ANNOUNCEMENTS[idx]['text'])
        ANNOUNCEMENTS[idx]['date'] = datetime.now().strftime('%d.%m.%Y %H:%M')
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route('/api/announcement/<int:idx>', methods=['DELETE'])
def delete_announcement(idx):
    if 0 <= idx < len(ANNOUNCEMENTS):
        ANNOUNCEMENTS.pop(idx)
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route('/api/announcement/move/<int:idx>', methods=['POST'])
def move_announcement(idx):
    direction = request.args.get('direction', '')
    if 0 <= idx < len(ANNOUNCEMENTS):
        if direction == 'up' and idx > 0:
            ANNOUNCEMENTS[idx], ANNOUNCEMENTS[idx-1] = ANNOUNCEMENTS[idx-1], ANNOUNCEMENTS[idx]
        elif direction == 'down' and idx < len(ANNOUNCEMENTS)-1:
            ANNOUNCEMENTS[idx], ANNOUNCEMENTS[idx+1] = ANNOUNCEMENTS[idx+1], ANNOUNCEMENTS[idx]
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

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
