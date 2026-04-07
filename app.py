import streamlit as st
import base64
import io
import requests
import tempfile
import os
from PIL import Image
from groq import Groq
from gtts import gTTS

st.set_page_config(page_title="Crop Disease Detector", layout="centered")
st.markdown("<h1 style='text-align:center;color:#2d6a4f;'>🌿 Crop Disease Detector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#52b788;font-size:18px;'>AI-powered disease detection for farmers — Free & Instant</p>", unsafe_allow_html=True)
st.markdown("---")

def get_weather_risk(city="Salem"):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
        data = r.json()
        humidity = int(data['current_condition'][0]['humidity'])
        temp = int(data['current_condition'][0]['temp_C'])
        desc = data['current_condition'][0]['weatherDesc'][0]['value']
        if humidity > 80 and temp > 25:
            risk = "🔴 HIGH"
            advice = "High humidity + heat = disease spreads fast today! Spray fungicide immediately."
        elif humidity > 60:
            risk = "🟠 MEDIUM"
            advice = "Moderate humidity. Monitor your crops closely today."
        else:
            risk = "🟢 LOW"
            advice = "Good weather. Low disease spread risk today."
        return humidity, temp, desc, risk, advice
    except:
        return None, None, None, None, None

humidity, temp, desc, risk, advice = get_weather_risk()
if risk:
    st.markdown("### 🌦️ Today's Disease Spread Risk — Salem, TN")
    w1, w2, w3 = st.columns(3)
    w1.metric("🌡️ Temp", f"{temp}°C")
    w2.metric("💧 Humidity", f"{humidity}%")
    w3.metric("⚠️ Risk", risk)
    if "HIGH" in risk:
        st.error(f"⚠️ {advice}")
    elif "MEDIUM" in risk:
        st.warning(f"⚠️ {advice}")
    else:
        st.success(f"✅ {advice}")
    st.markdown("---")

api_key = st.secrets.get("GROQ_API_KEY", "")
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.markdown("### 📸 Step 1\nUpload leaf photo")
col2.markdown("### 🔬 Step 2\nAI detects disease")
col3.markdown("### 💊 Step 3\nGet medicine & cure")
st.markdown("---")

uploaded = st.file_uploader("📸 Upload a leaf photo", type=["jpg","jpeg","png"])

if uploaded and api_key:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="📸 Uploaded Leaf", use_container_width=True)

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

   with st.spinner("🔬 AI analyzing leaf..."):
                   model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    {"type": "text", "text": "You are an expert plant pathologist helping Indian farmers. Analyze this leaf image carefully. Respond in EXACTLY this format, ALL fields required:\nCROP: [crop name]\nDISEASE: [disease name or Healthy]\nSEVERITY: [Mild/Moderate/Severe/None]\nCAUSE: [one sentence]\nMEDICINE_1: [medicine and dosage]\nMEDICINE_2: [alternative or None]\nHOW_TO_APPLY: [steps]\nWHEN_TO_SPRAY: [timing]\nPREVENTION: [2 tips]\nENGLISH: [2 sentence summary in English]\nTAMIL: [2 sentence summary in Tamil]\nHINDI: [2 sentence summary in Hindi]\nTELUGU: [2 sentence summary in Telugu]\nKANNADA: [2 sentence summary in Kannada]\n\nFill every field. No skipping."}
                ]
            }],
            max_tokens=1500
        )

    raw = response.choices[0].message.content.strip()
    data = {}
    for line in raw.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()

    disease  = data.get("DISEASE", "Unknown")
    crop     = data.get("CROP", "Unknown")
    severity = data.get("SEVERITY", "")
    cause    = data.get("CAUSE", "")
    med1     = data.get("MEDICINE_1", "")
    med2     = data.get("MEDICINE_2", "")
    how      = data.get("HOW_TO_APPLY", "")
    when     = data.get("WHEN_TO_SPRAY", "")
    prevent  = data.get("PREVENTION", "")
    lang_en  = data.get("ENGLISH", "")
    lang_ta  = data.get("TAMIL", "")
    lang_hi  = data.get("HINDI", "")
    lang_te  = data.get("TELUGU", "")
    lang_kn  = data.get("KANNADA", "")

    st.markdown("---")
    st.markdown("## 🔬 Step 2 — Disease Result")

    if "healthy" in disease.lower():
        st.success(f"✅ {crop} — Healthy! No disease detected.")
        st.info("Keep monitoring regularly.")
    else:
        sev_icon = {"Mild":"🟡","Moderate":"🟠","Severe":"🔴"}.get(severity,"🟠")
        c1, c2 = st.columns(2)
        c1.error(f"**🌾 Crop:** {crop}\n\n**🦠 Disease:** {disease}")
        c2.warning(f"**{sev_icon} Severity:** {severity}\n\n**📌 Cause:** {cause}")

        st.markdown("---")
        st.markdown("## 💊 Step 3 — Medicine & Treatment")
        m1, m2 = st.columns(2)
        m1.success(f"**💊 Medicine 1:**\n\n{med1}")
        if med2 and med2.lower() != "none":
            m2.success(f"**💊 Medicine 2:**\n\n{med2}")
        else:
            m2.info("No alternative needed")

        st.info(f"🧪 **How to Apply:** {how}")
        st.info(f"⏰ **When to Spray:** {when}")
        st.warning(f"🛡️ **Prevention:** {prevent}")

    st.markdown("---")
    st.markdown("## 🌍 5 Language Voice + Text")

    languages = [
        ("🇬🇧 English", lang_en, "en"),
        ("🇮🇳 Tamil",   lang_ta, "ta"),
        ("🇮🇳 Hindi",   lang_hi, "hi"),
        ("🇮🇳 Telugu",  lang_te, "te"),
        ("🇮🇳 Kannada", lang_kn, "kn"),
    ]

    for lang_name, lang_text, lang_code in languages:
        if lang_text:
            with st.expander(f"{lang_name} — click to read & listen"):
                st.write(lang_text)
                if st.button(f"🔊 Speak {lang_name}", key=f"btn_{lang_code}"):
                    try:
                        tts = gTTS(text=lang_text, lang=lang_code, slow=False)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                            tts.save(f.name)
                            fname = f.name
                        with open(fname, "rb") as af:
                            st.audio(af.read(), format="audio/mp3", autoplay=True)
                        os.unlink(fname)
                    except Exception as e:
                        st.warning(f"Voice error: {e}")

    st.markdown("---")
    st.caption("For guidance only. Verify with your local Krishi Vigyan Kendra (KVK).")

elif uploaded and not api_key:
    st.warning("Please enter your Groq API key above.")
else:
    st.markdown("""
    <div style='text-align:center;padding:40px;background:#f0fdf4;
    border-radius:12px;border:2px dashed #52b788;'>
        <h3 style='color:#2d6a4f;'>👆 Upload a leaf photo to begin</h3>
        <p style='color:#52b788;'>Supports 20+ crops — Results in 5 Indian languages</p>
        <p style='color:#888;'>Voice output in English, Tamil, Hindi, Telugu & Kannada</p>
    </div>
    """, unsafe_allow_html=True)