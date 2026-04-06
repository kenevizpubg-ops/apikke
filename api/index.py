from flask import Flask, request, jsonify, render_template_string, session
import requests
import base64
import random
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "keneviz_gizli_anahtar_2026"

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
        "desc": "Kullanıcı bilgisi sorgula • tg nick ve yaş",
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

ZIYARETCI_SAYISI = 0
AKTIF_KULLANICILAR = {}
DUYURULAR = []
API_KULLANIM = {}
GIRIS_KAYITLARI = []

def yeni_id_uret():
    if not APIS_DB:
        return 1
    return max(APIS_DB.keys()) + 1

def kayit_ekle(islem, detay=""):
    GIRIS_KAYITLARI.append({
        'islem': islem,
        'detay': detay,
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'cihaz': request.headers.get('User-Agent', 'Bilinmiyor')[:50],
        'zaman': datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    })
    if len(GIRIS_KAYITLARI) > 100:
        GIRIS_KAYITLARI.pop(0)

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

        body {
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            min-height: 100vh;
            padding: 20px;
            transition: all 0.3s ease;
        }

        body.dark {
            background: #0a0a0a;
            color: #00ff00;
        }

        body.light {
            background: linear-gradient(135deg, #f5f0ff 0%, #fce4ec 50%, #e8eaf6 100%);
            color: #333;
        }

        body.light .ust,
        body.light .kart,
        body.light .api-kart,
        body.light .duyuru,
        body.light .modal-icerik {
            background: white;
            color: #333;
            border-color: #9b59b6;
        }

        body.dark .ust,
        body.dark .kart,
        body.dark .api-kart,
        body.dark .duyuru,
        body.dark .modal-icerik {
            background: rgba(0, 20, 0, 0.85);
            border-color: #00ff00;
        }

        .kapsayici {
            max-width: 1400px;
            margin: 0 auto;
        }

        .ust {
            text-align: center;
            margin-bottom: 30px;
            position: relative;
            padding: 20px;
            border-radius: 20px;
            border: 2px solid;
            backdrop-filter: blur(5px);
        }

        body.dark .ust {
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }

        body.light .ust {
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }

        .logo {
            font-size: 3em;
            font-weight: bold;
        }

        body.dark .logo {
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }

        body.light .logo {
            background: linear-gradient(135deg, #9b59b6, #e91e63, #2196f3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .alt-yazi {
            margin-top: 10px;
            font-size: 0.9em;
            opacity: 0.8;
            cursor: pointer;
        }

        .tema-buton {
            position: relative;
            margin-bottom: 20px;
            background: transparent;
            border: 2px solid;
            border-radius: 30px;
            padding: 8px 20px;
            cursor: pointer;
            font-family: monospace;
            font-weight: bold;
            transition: all 0.3s;
        }

        body.dark .tema-buton {
            color: #00ff00;
            border-color: #00ff00;
        }

        body.light .tema-buton {
            color: #9b59b6;
            border-color: #9b59b6;
        }

        .tema-buton:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px currentColor;
        }

        .istatistikler {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .kart {
            border-radius: 20px;
            padding: 15px 30px;
            text-align: center;
            border: 1px solid;
            backdrop-filter: blur(5px);
        }

        body.dark .kart {
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }

        body.light .kart {
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }

        .kart h3 {
            font-size: 0.75em;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        body.light .kart h3 {
            color: #e91e63;
        }

        body.dark .kart h3 {
            color: #00ff88;
        }

        .kart .sayi {
            font-size: 2.2em;
            font-weight: bold;
        }

        body.dark .kart .sayi {
            text-shadow: 0 0 5px #00ff00;
        }

        body.light .kart .sayi {
            color: #6c5ce7;
        }

        .duyuru {
            border-radius: 15px;
            padding: 15px 25px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
            border: 1px solid;
        }

        body.dark .duyuru {
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }

        body.light .duyuru {
            background: linear-gradient(135deg, #f5f0ff, #fce4ec);
        }

        .duyuru .ikon { font-size: 1.5em; }
        .duyuru .metin { flex: 1; font-size: 0.95em; }
        .duyuru .tarih { font-size: 0.7em; opacity: 0.8; }

        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }

        .api-kart {
            border-radius: 20px;
            padding: 20px;
            transition: all 0.3s;
            border: 1px solid;
            backdrop-filter: blur(5px);
        }

        .api-kart:hover {
            transform: translateY(-5px);
        }

        body.dark .api-kart:hover {
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }

        body.light .api-kart:hover {
            box-shadow: 0 5px 20px rgba(155, 89, 182, 0.15);
        }

        .api-baslik {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }

        .api-icon { font-size: 2em; }
        .api-isim {
            font-size: 1.2em;
            font-weight: bold;
        }

        body.dark .api-isim {
            text-shadow: 0 0 5px #00ff00;
            color: #00ffff;
        }

        body.light .api-isim {
            color: #6c5ce7;
        }

        .api-id {
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 0.65em;
            margin-left: 8px;
        }

        body.light .api-id {
            background: #e8eaf6;
            color: #5e35b1;
        }

        body.dark .api-id {
            background: rgba(0,255,0,0.2);
            color: #00ff00;
        }

        .api-durum {
            margin-left: auto;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.65em;
            border: 1px solid;
        }

        body.dark .api-durum {
            color: #00ff88;
            border-color: #00ff88;
            background: rgba(0,255,0,0.2);
        }

        body.light .api-durum {
            background: #e8f5e9;
            color: #4caf50;
            border-color: #4caf50;
        }

        .api-aciklama {
            font-size: 0.85em;
            margin-bottom: 15px;
            line-height: 1.4;
            opacity: 0.8;
        }

        .param-grup {
            margin-bottom: 12px;
        }

        .param-grup label {
            display: block;
            font-size: 0.75em;
            margin-bottom: 5px;
            font-weight: 600;
        }

        body.light .param-grup label {
            color: #9b59b6;
        }

        body.dark .param-grup label {
            color: #00ff88;
        }

        .param-grup input {
            width: 100%;
            padding: 10px 14px;
            background: rgba(0,0,0,0.5);
            border-radius: 12px;
            font-size: 0.9em;
            transition: all 0.3s;
        }

        body.dark .param-grup input {
            border: 1px solid #00ff00;
            color: #00ff00;
        }

        body.light .param-grup input {
            border: 1px solid #ddd;
            color: #333;
            background: #fafafa;
        }

        .param-grup input:focus {
            outline: none;
            box-shadow: 0 0 10px currentColor;
        }

        .buton-grup {
            display: flex;
            gap: 12px;
            margin-top: 15px;
        }

        .sorgula-btn {
            flex: 2;
            padding: 12px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85em;
            transition: all 0.3s;
        }

        body.dark .sorgula-btn {
            background: #00ff00;
            color: #0a0a0a;
            border: none;
        }

        body.light .sorgula-btn {
            background: linear-gradient(135deg, #9b59b6, #e91e63);
            color: white;
            border: none;
        }

        .url-btn {
            flex: 1;
            padding: 12px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: bold;
            transition: all 0.3s;
        }

        body.dark .url-btn {
            background: transparent;
            color: #00ff00;
            border: 1px solid #00ff00;
        }

        body.light .url-btn {
            background: linear-gradient(135deg, #2196f3, #00bcd4);
            color: white;
            border: none;
        }

        .sorgula-btn:hover, .url-btn:hover {
            transform: scale(0.98);
            opacity: 0.9;
        }

        .sonuc {
            margin-top: 15px;
            padding: 12px;
            background: rgba(0,0,0,0.6);
            border-radius: 12px;
            max-height: 300px;
            overflow-y: auto;
            display: none;
            font-size: 0.8em;
            border: 1px solid;
        }

        body.dark .sonuc {
            border-color: #00ff00;
        }

        body.light .sonuc {
            border-color: #ddd;
            background: #f8f9fa;
        }

        .sonuc.show { display: block; }
        .sonuc pre {
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 0.75em;
        }

        body.dark .sonuc pre { color: #00ff00; }
        body.light .sonuc pre { color: #333; }

        .sonuc-resim { max-width: 100%; border-radius: 10px; }
        .sonuc-ses { width: 100%; }

        .yukleme {
            text-align: center;
            padding: 10px;
            display: none;
            font-size: 0.85em;
        }

        .yukleme.show { display: block; }

        .alt {
            text-align: center;
            padding: 20px;
            font-size: 0.75em;
            border-top: 1px solid;
            opacity: 0.6;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }

        .modal.show { display: flex; }

        .modal-icerik {
            border-radius: 20px;
            padding: 25px;
            width: 550px;
            max-width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            border: 2px solid;
        }

        .modal-icerik h3, .modal-icerik h4 {
            margin-bottom: 15px;
        }

        .modal-icerik input, .modal-icerik textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 12px;
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
        }

        body.dark .modal-icerik input,
        body.dark .modal-icerik textarea {
            border: 1px solid #00ff00;
            color: #00ff00;
        }

        body.light .modal-icerik input,
        body.light .modal-icerik textarea {
            border: 1px solid #ddd;
            color: #333;
            background: #fafafa;
        }

        .modal-icerik button {
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
            font-family: monospace;
        }

        body.dark .modal-icerik button {
            background: #00ff00;
            color: #0a0a0a;
            border: none;
        }

        body.light .modal-icerik button {
            background: linear-gradient(135deg, #9b59b6, #e91e63);
            color: white;
            border: none;
        }

        .kapat-btn {
            float: right;
        }

        .duyuru-ogesi {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            border: 1px solid;
        }

        .duyuru-ogesi button {
            padding: 5px 10px;
            font-size: 0.7em;
        }

        hr { margin: 15px 0; }
        .cikis-btn { margin-top: 10px; }

        .modal-baslik {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        body.dark ::-webkit-scrollbar-track { background: #0a0a0a; }
        body.dark ::-webkit-scrollbar-thumb { background: #00ff00; border-radius: 4px; }
        body.light ::-webkit-scrollbar-track { background: #f1f1f1; }
        body.light ::-webkit-scrollbar-thumb { background: #9b59b6; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="kapsayici">
        <div class="ust">
            <div class="logo">KENEVİZ API PORTAL</div>
            <div class="alt-yazi" id="hackerYazi">⚡ BEYAZ ŞAPKALI ⚡</div>
            <div class="dev-tag">GELİŞTİRİCİ : KENEViZ</div>
        </div>

        <div style="text-align:center; margin-bottom:20px;">
            <button class="tema-buton" onclick="temaDegistir()">🌓 TEMA DEĞİŞTİR</button>
        </div>

        <div class="istatistikler">
            <div class="kart"><h3>👥 ZİYARETÇİ</h3><div class="sayi">{{ visitor_count }}</div></div>
            <div class="kart"><h3>🟢 AKTİF</h3><div class="sayi">{{ active_count }}</div></div>
            <div class="kart"><h3>📊 API</h3><div class="sayi">{{ apis|length }}</div></div>
            <div class="kart"><h3>⚡ HİZMET</h3><div class="sayi">24/7</div></div>
        </div>

        {% if announcement %}
        <div class="duyuru">
            <div class="ikon">📢</div>
            <div class="metin">{{ announcement.text }}</div>
            <div class="tarih">{{ announcement.date }}</div>
        </div>
        {% endif %}

        <div class="api-grid" id="apiGrid"></div>

        <div class="alt">
            <p>⚡ KENEVIZ API PORTAL • @KenevizOrjin</p>
            <p>📌 14+ API | 7/24 HİZMET</p>
            <p>✈️ Telegram : @KenevizVipApiService</p>
        </div>
    </div>

    <div id="yonetimModal" class="modal">
        <div class="modal-icerik">
            <div class="modal-baslik">
                <h3>🔧 KENEVIZ AYARLARI</h3>
                <button class="kapat-btn" onclick="kapatModal()">❌</button>
            </div>
            {% if session.get('yonetici_girisi') %}
                <div style="text-align:center; margin-bottom:15px;">
                    <span style="color:#00ff88;">✅ Yetki aktif</span>
                    <button class="cikis-btn" onclick="cikisYap()">🚪 ÇIKIŞ</button>
                </div>
                <div id="yetkiPaneli">
                    <h4>📢 DUYURU YÖNETİMİ</h4>
                    <textarea id="yeniDuyuru" rows="2" placeholder="Yeni duyuru metni..."></textarea>
                    <button onclick="duyuruEkle()">➕ YENİ DUYURU EKLE</button>
                    <div id="duyuruListesi" style="margin-top:15px;"></div>
                    <hr>
                    <h4>➕ YENİ API EKLE</h4>
                    <input type="text" id="apiAd" placeholder="API Adı">
                    <input type="text" id="apiUrl" placeholder="Endpoint URL">
                    <textarea id="apiParametre" rows="2" placeholder='{"param": ""}'></textarea>
                    <input type="text" id="apiMetod" value="GET">
                    <input type="text" id="apiTip" value="json">
                    <input type="text" id="apiIcon" value="🔧">
                    <input type="text" id="apiTanim" placeholder="Açıklama">
                    <button onclick="apiEkle()">➕ EKLE</button>
                    <hr>
                    <h4>🗑️ API SİL</h4>
                    <input type="number" id="silinecekId" placeholder="API ID (örn: 1, 2, 3...)">
                    <button onclick="apiSil()">🗑️ SİL</button>
                    <hr>
                    <h4>📋 GİRİŞ KAYITLARI</h4>
                    <button onclick="kayitlariGoster()">📋 KAYITLARI GÖSTER</button>
                    <pre id="kayitListesi" style="margin-top:10px; background:rgba(0,0,0,0.5); padding:10px; border-radius:10px; font-size:0.7em; display:none; max-height:200px; overflow:auto;"></pre>
                </div>
            {% else %}
                <input type="password" id="girisKodu" placeholder="Yetki Kodu">
                <button onclick="yetkiKontrol()">GİRİŞ YAP</button>
                <button onclick="kapatModal()">KAPAT</button>
            {% endif %}
        </div>
    </div>

    <script>
        let apiVerileri = {{ apis|tojson|safe }};
        let apiKullanim = {{ api_usage|tojson|safe }};
        let duyuruList = {{ announcements|tojson|safe }};
        let yoneticiGirisi = {{ 'true' if session.get('yonetici_girisi') else 'false' }};

        function hackerYaziGuncelle() {
            const yazi = document.getElementById('hackerYazi');
            if (document.body.classList.contains('dark')) {
                yazi.innerHTML = '⚡ SİYAH ŞAPKALI ⚡';
            } else {
                yazi.innerHTML = '⚡ BEYAZ ŞAPKALI ⚡';
            }
        }

        function temaDegistir() {
            if (document.body.classList.contains('dark')) {
                document.body.classList.remove('dark');
                document.body.classList.add('light');
                localStorage.setItem('tema', 'light');
            } else {
                document.body.classList.remove('light');
                document.body.classList.add('dark');
                localStorage.setItem('tema', 'dark');
            }
            hackerYaziGuncelle();
        }

        if (localStorage.getItem('tema') === 'light') {
            document.body.classList.add('light');
        } else {
            document.body.classList.add('dark');
        }
        hackerYaziGuncelle();

        let tikSayaci = 0;
        let sonTikZamani = 0;

        function gizliTetikleyici() {
            const simdi = new Date().getTime();
            if (simdi - sonTikZamani > 2000) tikSayaci = 0;
            sonTikZamani = simdi;
            tikSayaci++;
            
            if (yoneticiGirisi) {
                if (tikSayaci === 5) {
                    tikSayaci = 0;
                    document.getElementById('yonetimModal').classList.add('show');
                    duyuruListele();
                }
            } else {
                if (tikSayaci === 25) {
                    tikSayaci = 0;
                    document.getElementById('yonetimModal').classList.add('show');
                }
            }
        }

        document.getElementById('hackerYazi').addEventListener('click', gizliTetikleyici);

        function kapatModal() {
            document.getElementById('yonetimModal').classList.remove('show');
        }

        async function yetkiKontrol() {
            const kod = document.getElementById('girisKodu').value;
            const cevap = await fetch('/api/admin/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key: kod })
            });
            const veri = await cevap.json();
            if (veri.success) {
                location.reload();
            } else {
                alert('❌ Hatalı Kod!');
            }
        }

        async function cikisYap() {
            await fetch('/api/admin/logout', { method: 'POST' });
            location.reload();
        }

        function apiListele() {
            const grid = document.getElementById('apiGrid');
            grid.innerHTML = '';
            for (const [id, api] of Object.entries(apiVerileri)) {
                let parametreHtml = '';
                for (const [pAd, pDeger] of Object.entries(api.params || {})) {
                    parametreHtml += `<div class="param-grup">
                        <label>${pAd}:</label>
                        <input type="text" data-param="${pAd}" placeholder="${pDeger}">
                    </div>`;
                }
                let kullanim = apiKullanim[id] || 0;
                grid.innerHTML += `
                    <div class="api-kart" data-api-id="${id}">
                        <div class="api-baslik">
                            <div class="api-icon">${api.icon || '🔧'}</div>
                            <div class="api-isim">${api.name} <span class="api-id">ID:${id}</span></div>
                            <div class="api-durum">HAZIR</div>
                        </div>
                        <div class="api-aciklama">${api.desc || ''}</div>
                        <div class="api-aciklama" style="opacity:0.7; font-size:0.7em;">📊 Kullanım: ${kullanim} kez</div>
                        ${parametreHtml}
                        <div class="buton-grup">
                            <button class="sorgula-btn" onclick="apiSorgula(${id})">🚀 SORGULA</button>
                            <button class="url-btn" onclick="urlAc(${id})">🔗 URL</button>
                        </div>
                        <div class="yukleme" id="yukleme-${id}">⏳ İşleniyor...</div>
                        <div class="sonuc" id="sonuc-${id}"></div>
                    </div>
                `;
            }
        }

        async function apiSorgula(apiId) {
            const kart = document.querySelector(`.api-kart[data-api-id="${apiId}"]`);
            const parametreler = {};
            kart.querySelectorAll('.param-grup input').forEach(inp => {
                const pAd = inp.getAttribute('data-param');
                if (inp.value) parametreler[pAd] = inp.value;
            });

            const yuklemeDiv = document.getElementById(`yukleme-${apiId}`);
            const sonucDiv = document.getElementById(`sonuc-${apiId}`);
            yuklemeDiv.classList.add('show');
            sonucDiv.classList.remove('show');
            sonucDiv.innerHTML = '';

            try {
                const cevap = await fetch(`/api/query/${apiId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ params: parametreler })
                });
                const veri = await cevap.json();
                if (veri.success) {
                    if (veri.response_type === 'image') {
                        sonucDiv.innerHTML = `<img src="data:${veri.content_type};base64,${veri.image_base64}" class="sonuc-resim">`;
                    } else if (veri.response_type === 'audio') {
                        sonucDiv.innerHTML = `<audio controls src="data:${veri.content_type};base64,${veri.audio_base64}" class="sonuc-ses"></audio>`;
                    } else {
                        sonucDiv.innerHTML = `<pre>${JSON.stringify(veri.data, null, 2)}</pre>`;
                    }
                    await fetch(`/api/usage/${apiId}`, { method: 'POST' });
                    const kullanimSpan = kart.querySelector('.api-aciklama[style*="opacity:0.7"]');
                    if (kullanimSpan) {
                        let mevcut = apiKullanim[apiId] || 0;
                        apiKullanim[apiId] = mevcut + 1;
                        kullanimSpan.innerHTML = `📊 Kullanım: ${apiKullanim[apiId]} kez`;
                    }
                } else {
                    sonucDiv.innerHTML = `<pre style="color:#ff3366;">❌ HATA: ${veri.error}</pre>`;
                }
                sonucDiv.classList.add('show');
            } catch(e) {
                sonucDiv.innerHTML = `<pre style="color:#ff3366;">❌ HATA: ${e.message}</pre>`;
                sonucDiv.classList.add('show');
            } finally {
                yuklemeDiv.classList.remove('show');
            }
        }

        function urlAc(apiId) {
            const api = apiVerileri[apiId];
            if (api) window.open(api.endpoint, '_blank');
        }

        function duyuruListele() {
            const liste = document.getElementById('duyuruListesi');
            if (!liste) return;
            liste.innerHTML = '<h5>Mevcut Duyurular:</h5>';
            duyuruList.forEach((duyuru, index) => {
                liste.innerHTML += `
                    <div class="duyuru-ogesi">
                        <div class="metin">${duyuru.text}</div>
                        <div class="tarih">${duyuru.date}</div>
                        <button onclick="duyuruDuzenle(${index})">✏️ Düzenle</button>
                        <button onclick="duyuruSil(${index})">🗑️ Sil</button>
                        <button onclick="duyuruTasi(${index}, 'up')">⬆️</button>
                        <button onclick="duyuruTasi(${index}, 'down')">⬇️</button>
                    </div>
                `;
            });
        }

        async function duyuruEkle() {
            const metin = document.getElementById('yeniDuyuru').value;
            if (!metin) { alert('Duyuru metni girin!'); return; }
            const cevap = await fetch('/api/announcement', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: metin })
            });
            const veri = await cevap.json();
            if (veri.success) {
                alert('Duyuru eklendi!');
                location.reload();
            }
        }

        async function duyuruDuzenle(index) {
            const yeniMetin = prompt('Yeni duyuru metni:', duyuruList[index].text);
            if (yeniMetin) {
                const cevap = await fetch(`/api/announcement/${index}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: yeniMetin })
                });
                if (cevap.ok) location.reload();
            }
        }

        async function duyuruSil(index) {
            if (confirm('Duyuru silinsin mi?')) {
                await fetch(`/api/announcement/${index}`, { method: 'DELETE' });
                location.reload();
            }
        }

        async function duyuruTasi(index, yon) {
            await fetch(`/api/announcement/move/${index}?direction=${yon}`, { method: 'POST' });
            location.reload();
        }

        async function kayitlariGoster() {
            const cevap = await fetch('/api/admin/logs');
            const kayitlar = await cevap.json();
            const kayitDiv = document.getElementById('kayitListesi');
            kayitDiv.style.display = 'block';
            kayitDiv.innerHTML = kayitlar.map(k => 
                `[${k.zaman}] ${k.islem} - IP:${k.ip} - ${k.detay}`
            ).join('\\n');
        }

        async function apiEkle() {
            let parametreler = {};
            try { parametreler = JSON.parse(document.getElementById('apiParametre').value || '{}'); } catch(e) {}
            const cevap = await fetch('/api/admin/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: document.getElementById('apiAd').value,
                    endpoint: document.getElementById('apiUrl').value,
                    params: parametreler,
                    method: document.getElementById('apiMetod').value,
                    desc: document.getElementById('apiTanim').value,
                    response_type: document.getElementById('apiTip').value,
                    icon: document.getElementById('apiIcon').value
                })
            });
            const veri = await cevap.json();
            if (veri.success) { alert('API eklendi! ID: ' + veri.api_id); location.reload(); }
            else { alert('Hata: ' + veri.error); }
        }

        async function apiSil() {
            const id = document.getElementById('silinecekId').value;
            if (!id) { alert('API ID girin!'); return; }
            
            const apiAdi = apiVerileri[id] ? apiVerileri[id].name : 'Bilinmeyen API';
            
            const cevap = await fetch(`/api/admin/delete/${id}`, { method: 'DELETE' });
            const veri = await cevap.json();
            if (veri.success) { 
                alert(`✅ API silindi! Silinen: ${apiAdi} (ID:${id})`);
                location.reload();
            } else { 
                alert('❌ Hata: ' + veri.error); 
            }
        }

        apiListele();

        setInterval(() => {
            fetch('/api/heartbeat', { method: 'POST' });
        }, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    global ZIYARETCI_SAYISI
    ZIYARETCI_SAYISI += 1
    
    oturum_id = request.headers.get('User-Agent', str(random.random()))
    AKTIF_KULLANICILAR[oturum_id] = time.time()
    
    simdi = time.time()
    gecici = [k for k, v in AKTIF_KULLANICILAR.items() if simdi - v > 300]
    for k in gecici:
        del AKTIF_KULLANICILAR[k]
    
    son_duyuru = DUYURULAR[-1] if DUYURULAR else None
    
    return render_template_string(HTML_TEMPLATE, 
                                  apis=APIS_DB,
                                  visitor_count=ZIYARETCI_SAYISI,
                                  active_count=len(AKTIF_KULLANICILAR),
                                  announcement=son_duyuru,
                                  announcements=DUYURULAR,
                                  api_usage=API_KULLANIM)

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    girilen_kod = str(data.get('key', '')).strip()
    saat_sifresi = str(datetime.now().hour)
    
    if girilen_kod == saat_sifresi:
        session['yonetici_girisi'] = True
        kayit_ekle('GİRİŞ YAPTI', 'Başarılı giriş')
        return jsonify({"success": True})
    kayit_ekle('BAŞARISIZ GİRİŞ', f"Yanlış kod: {girilen_kod}")
    return jsonify({"success": False}), 401

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    kayit_ekle('ÇIKIŞ YAPTI', 'Oturum sonlandırıldı')
    session.clear()
    return jsonify({"success": True})

@app.route('/api/admin/logs', methods=['GET'])
def get_logs():
    if not session.get('yonetici_girisi'):
        return jsonify({"error": "Yetkisiz"}), 401
    return jsonify(GIRIS_KAYITLARI[-50:])

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    oturum_id = request.headers.get('User-Agent', str(random.random()))
    AKTIF_KULLANICILAR[oturum_id] = time.time()
    return jsonify({"success": True})

@app.route('/api/announcement', methods=['POST'])
def add_announcement():
    if not session.get('yonetici_girisi'):
        return jsonify({"error": "Yetkisiz"}), 401
    data = request.json
    text = data.get('text', '')
    if text:
        DUYURULAR.append({
            'text': text,
            'date': datetime.now().strftime('%d.%m.%Y %H:%M')
        })
        kayit_ekle('DUYURU EKLENDİ', text[:50])
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/api/announcement/<int:idx>', methods=['PUT'])
def edit_announcement(idx):
    if not session.get('yonetici_girisi'):
        return jsonify({"error": "Yetkisiz"}), 401
    if 0 <= idx < len(DUYURULAR):
        data = request.json
        eski_metin = DUYURULAR[idx]['text']
        DUYURULAR[idx]['text'] = data.get('text', eski_metin)
        DUYURULAR[idx]['date'] = datetime.now().strftime('%d.%m.%Y %H:%M')
        kayit_ekle('DUYURU DÜZENLENDİ', f"Eski: {eski_metin[:30]} -> Yeni: {data.get('text', '')[:30]}")
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route('/api/announcement/<int:idx>', methods=['DELETE'])
def delete_announcement(idx):
    if not session.get('yonetici_girisi'):
        return jsonify({"error": "Yetkisiz"}), 401
    if 0 <= idx < len(DUYURULAR):
        silinen = DUYURULAR.pop(idx)
        kayit_ekle('DUYURU SİLİNDİ', silinen['text'][:50])
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route('/api/announcement/move/<int:idx>', methods=['POST'])
def move_announcement(idx):
    if not session.get('yonetici_girisi'):
        return jsonify({"error": "Yetkisiz"}), 401
    direction = request.args.get('direction', '')
    if 0 <= idx < len(DUYURULAR):
        if direction == 'up' and idx > 0:
            DUYURULAR[idx], DUYURULAR[idx-1] = DUYURULAR[idx-1], DUYURULAR[idx]
            kayit_ekle('DUYURU TAŞINDI', f"{idx+1}. duyuru yukarı taşındı")
        elif direction == 'down' and idx < len(DUYURULAR)-1:
            DUYURULAR[idx], DUYURULAR[idx+1] = DUYURULAR[idx+1], DUYURULAR[idx]
            kayit_ekle('DUYURU TAŞINDI', f"{idx+1}. duyuru aşağı taşındı")
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route('/api/query/<int:api_id>', methods=['POST'])
def query_api(api_id):
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    
    API_KULLANIM[str(api_id)] = API_KULLANIM.get(str(api_id), 0) + 1
    
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
    API_KULLANIM[str(api_id)] = API_KULLANIM.get(str(api_id), 0) + 1
    return jsonify({"success": True})

@app.route('/api/admin/add', methods=['POST'])
def add_api():
    if not session.get('yonetici_girisi'):
        return jsonify({"error": "Yetkisiz"}), 401
    
    data = request.json
    if not data.get('endpoint'):
        return jsonify({"error": "Endpoint gerekli"}), 400
    
    new_id = yeni_id_uret()
    APIS_DB[new_id] = {
        "name": data.get('name', 'Yeni API'),
        "endpoint": data['endpoint'],
        "params": data.get('params', {}),
        "method": data.get('method', 'GET'),
        "desc": data.get('desc', ''),
        "response_type": data.get('response_type', 'json'),
        "icon": data.get('icon', '🔧')
    }
    kayit_ekle('API EKLENDİ', f"ID:{new_id} - {data.get('name', 'Yeni API')}")
    return jsonify({"success": True, "api_id": new_id})

@app.route('/api/admin/delete/<int:api_id>', methods=['DELETE'])
def delete_api(api_id):
    if not session.get('yonetici_girisi'):
        return jsonify({"error": "Yetkisiz"}), 401
    
    if api_id not in APIS_DB:
        return jsonify({"error": "API bulunamadı"}), 404
    
    api_name = APIS_DB[api_id].get('name', 'Bilinmeyen API')
    del APIS_DB[api_id]
    kayit_ekle('API SİLİNDİ', f"ID:{api_id} - {api_name}")
    return jsonify({"success": True, "deleted_name": api_name})

if __name__ == '__main__':
    app.run(port=8080)
