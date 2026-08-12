import streamlit as st
from google import genai
from PIL import Image

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="faress3rat",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. جلب المفتاح تلقائياً من إعدادات Streamlit السريّة (Secrets)
API_KEY = None
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = str(st.secrets["GEMINI_API_KEY"]).strip()

# 3. إدارة جلسة المستخدم
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "users_db" not in st.session_state:
    st.session_state["users_db"] = {"user": "1234"}

# 4. التنسيق وإخفاء القائمة الجانبية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    
    .hero-banner {
        background: linear-gradient(135deg, #0ba360 0%, #3cba92 100%);
        padding: 35px 20px;
        border-radius: 18px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .hero-banner h1 { color: white !important; font-size: 36px; margin: 0; }
    .hero-banner .sub-title {
        font-size: 20px;
        font-weight: bold;
        background-color: rgba(255, 255, 255, 0.2);
        display: inline-block;
        padding: 6px 20px;
        border-radius: 20px;
        margin-top: 12px;
    }
    
    .main-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .main-header h1 { color: white !important; font-size: 28px; margin: 0; }
    
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e9ecef;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 22px; font-weight: bold; color: #11998e; }
    .metric-label { font-size: 13px; color: #6c757d; }
    </style>
""", unsafe_allow_html=True)

# --- شاشة التسجيل / الدخول ---
if not st.session_state["logged_in"]:
    st.markdown("""
        <div class="hero-banner">
            <h1>🥗 faress3rat</h1>
            <div class="sub-title">✨ خيارك الأنسب ✨</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔐 تسجيل الدخول", "✨ إنشاء حساب جديد"])
        
        with tab_login:
            st.write(" ")
            login_user = st.text_input("اسم المستخدم:", key="login_u")
            login_pass = st.text_input("كلمة المرور:", type="password", key="login_p")
            
            if st.button("تسجيل الدخول 🚀", use_container_width=True):
                if login_user in st.session_state["users_db"] and st.session_state["users_db"][login_user] == login_pass:
                    st.session_state["logged_in"] = True
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")

        with tab_signup:
            st.write(" ")
            new_user = st.text_input("اختر اسم المستخدم:", key="signup_u")
            new_pass = st.text_input("اختر كلمة المرور:", type="password", key="signup_p")
            confirm_pass = st.text_input("تأكيد كلمة المرور:", type="password", key="signup_cp")
            
            if st.button("إنشاء الحساب والدخول فوراً 🎯", use_container_width=True):
                if not new_user or not new_pass:
                    st.warning("يرجى ملء جميع الحقول!")
                elif new_user in st.session_state["users_db"]:
                    st.error("اسم المستخدم هذا مستخدم بالفعل!")
                elif new_pass != confirm_pass:
                    st.error("كلمتا المرور غير متطابقتين!")
                else:
                    st.session_state["users_db"][new_user] = new_pass
                    st.session_state["logged_in"] = True
                    st.success("تم إنشاء الحساب بنجاح!")
                    st.rerun()

else:
    # --- التطبيق الرئيسي ---
    col_h1, col_h2 = st.columns([5, 1])
    with col_h2:
        if st.button("تسجيل الخروج 🚪"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.markdown("""
        <div class="main-header">
            <h1>🥗 faress3rat</h1>
            <p>حاسبة السعرات الحرارية وتحليل الوجبات بالذكاء الاصطناعي</p>
        </div>
    """, unsafe_allow_html=True)

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
                st.error("⚠️ لم يتم ضبط مفتاح Gemini API Key في Streamlit Secrets.")
            else:
                with st.spinner("جاري تحليل الوجبة... ⏳"):
                    try:
                        client = genai.Client(api_key=API_KEY)
                        prompt = "أنت أخصائي تغذية خبير ومحترف. قم بتحليل الوجبة في الصورة بدقة باللغة العربية واذكر السعرات والماكروز والتفاصيل."
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[prompt, image]
                        )
                        st.success("تم التحليل بنجاح! 🎉")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء التحليل: {e}")

    st.markdown("---")

    # 3. المساعد الذكي
    st.subheader("💬 3. المساعد التغذوي الذكي")
    user_question = st.text_input("اسأل أي سؤال تغذوي:")
    if user_question:
        if not API_KEY:
            st.error("⚠️ لم يتم ضبط مفتاح Gemini API Key في Streamlit Secrets.")
        else:
            with st.spinner("جاري الإجابة..."):
                try:
                    client = genai.Client(api_key=API_KEY)
                    chat_prompt = f"أجب كأخصائي تغذية بأسلوب مشجع ومختصر باللغة العربية على السؤال التالي: {user_question}"
                    chat_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=chat_prompt
                    )
                    st.info(chat_response.text)
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
