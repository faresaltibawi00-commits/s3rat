import streamlit as st
from google import genai
from PIL import Image

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="FitAI | حاسبة وتتبع السعرات",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. جلب المفتاح تلقائياً من إعدادات Streamlit السريّة (Secrets)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None

# 3. نظام تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# 4. تحسين المظهر والتنسيق
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    .main-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white !important;
        font-size: 24px;
        margin: 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e9ecef;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: bold;
        color: #11998e;
    }
    .metric-label {
        font-size: 13px;
        color: #6c757d;
    }
    </style>
""", unsafe_allow_html=True)

# --- شاشة تسجيل الدخول ---
if not st.session_state["logged_in"]:
    st.markdown("""
        <div class="main-header">
            <h1>🔐 تسجيل الدخول إلى FitAI</h1>
            <p>يرجى تسجيل الدخول للوصول لحاسبة السعرات والذكاء الاصطناعي</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("اسم المستخدم:")
        password = st.text_input("كلمة المرور:", type="password")
        login_btn = st.button("تسجيل الدخول 🚀")
        
        if login_btn:
            if username == "user" and password == "1234":
                st.session_state["logged_in"] = True
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة! (الافتراضي: user / 1234)")

else:
    # --- التطبيق الرئيسي ---
    st.markdown("""
        <div class="main-header">
            <h1>🥗 FitAI — رفيقك التغذوي الذكي</h1>
            <p>احسب احتياجك اليومي، صور وجبتك بالذكاء الاصطناعي، وتتبع سعراتك!</p>
        </div>
    """, unsafe_allow_html=True)

    # القائمة الجانبية
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        if st.button("تسجيل الخروج 🚪"):
            st.session_state["logged_in"] = False
            st.rerun()

    # 1. حساب الاحتياج اليومي
    st.subheader("📊 1. حساب الاحتياج اليومي (TDEE)")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        gender = st.radio("الجنس:", ("ذكر", "أنثى"), horizontal=True)
        age = st.number_input("العمر:", min_value=10, max_value=100, value=25)
        weight = st.number_input("الوزن (كجم):", min_value=30.0, max_value=200.0, value=70.0)
    with col_c2:
        height = st.number_input("الطول (سم):", min_value=100.0, max_value=230.0, value=170.0)
        activity_level = st.selectbox(
            "مستوى النشاط:",
            ["خامل (بدون تمارين)", "نشاط خفيف (1-3 أيام)", "نشاط متوسط (3-5 أيام)", "نشاط عالٍ (6-7 أيام)"]
        )
        goal = st.selectbox("الهدف:", ["المحافظة على الوزن ⚖️", "تنشيف / إنقاص الوزن 📉", "تضخيم / زيادة الوزن 📈"])

    bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == "ذكر" else -161)
    act_map = {"خامل (بدون تمارين)": 1.2, "نشاط خفيف (1-3 أيام)": 1.375, "نشاط متوسط (3-5 أيام)": 1.55, "نشاط عالٍ (6-7 أيام)": 1.725}
    tdee = bmr * act_map[activity_level]

    if "تنشيف" in goal:
        target_calories = tdee - 500
    elif "تضخيم" in goal:
        target_calories = tdee + 400
    else:
        target_calories = tdee

    protein_g = (target_calories * 0.30) / 4
    carbs_g = (target_calories * 0.40) / 4
    fats_g = (target_calories * 0.30) / 9

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(target_calories)}</div><div class="metric-label">سعرة حرارية</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(protein_g)}g</div><div class="metric-label">بروتين</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(carbs_g)}g</div><div class="metric-label">كربوهيدرات</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(fats_g)}g</div><div class="metric-label">دهون</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # 2. تحليل الوجبة بالذكاء الاصطناعي
    st.subheader("📸 2. تحليل الوجبة بالذكاء الاصطناعي")

    uploaded_file = st.file_uploader("ارفع صورة الوجبة هنا...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="الوجبة المرفوعة", use_container_width=True)
        
        if st.button("✨ تحليل الوجبة وحساب السعرات بدقة"):
            if not API_KEY:
                st.error("⚠️ لم يتم ضبط مفتاح Gemini API Key في إعدادات Streamlit Secrets.")
            else:
                with st.spinner("جاري تحليل الوجبة... ⏳"):
                    client = genai.Client(api_key=API_KEY)
                    prompt = """
                    أنت أخصائي تغذية خبير ومحترف جداً. قم بتحليل الوجبة في الصورة بدقة عالية باللغة العربية:
                    
                    1. 🍽️ **اسم الوجبة والمكونات المفصلة:** (قدر أوزان المكونات بالجرام بشكل دقيق ومحسب).
                    2. 📊 **الماكروز والسعرات الحرارية الدقيقة:**
                       - السعرات الحرارية الإجمالية:
                       - البروتين (غرام):
                       - الكربوهيدرات (غرام):
                       - الدهون (غرام):
                    3. 💡 **تقييم صحي ونصيحة للوجبة.**
                    """
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[prompt, image]
                        )
                        st.success("تم التحليل بنجاح! 🎉")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"حدث خطأ: {e}")

    st.markdown("---")

    # 3. المساعد الذكي
    st.subheader("💬 3. المساعد التغذوي الذكي")
    user_question = st.text_input("اسأل أي سؤال تغذوي:")
    if user_question:
        if not API_KEY:
            st.error("⚠️ لم يتم ضبط مفتاح Gemini API Key في إعدادات Streamlit Secrets.")
        else:
            with st.spinner("جاري الإجابة..."):
                try:
                    client = genai.Client(api_key=API_KEY)
                    chat_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"أجب كأخصائي تغذية بأسلوب مشجع ومختصر باللغة العربية: {user_question}"
                    )
                    st.info(chat_response.text)
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
