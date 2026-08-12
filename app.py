import streamlit as st
from groq import Groq
import base64
import json
from PIL import Image

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="faress3rat",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. جلب مفتاح Groq
API_KEY = None
if "GROQ_API_KEY" in st.secrets:
    API_KEY = str(st.secrets["GROQ_API_KEY"]).strip()

# 3. إدارة جلسة المستخدم
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "users_db" not in st.session_state:
    st.session_state["users_db"] = {"user": "1234"}

# قيم عداد الوجبة المحللة
if "total_cals" not in st.session_state:
    st.session_state["total_cals"] = 0
if "total_protein" not in st.session_state:
    st.session_state["total_protein"] = 0
if "total_carbs" not in st.session_state:
    st.session_state["total_carbs"] = 0
if "total_fats" not in st.session_state:
    st.session_state["total_fats"] = 0
if "meal_name" not in st.session_state:
    st.session_state["meal_name"] = "لم يتم تحليل وجبة بعد"

# 4. التنسيق والتصميم الفخم
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    
    .hero-banner {
        background: linear-gradient(135deg, #0d3b66 0%, #00b4d8 100%);
        padding: 40px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .hero-banner h1 {
        color: #ffffff !important;
        font-size: 42px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 1px;
    }
    .hero-banner .sub-title {
        font-size: 18px;
        font-weight: 700;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
        display: inline-block;
        padding: 6px 24px;
        border-radius: 30px;
        margin-top: 12px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .main-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 25px;
        border-radius: 18px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white !important;
        font-size: 34px;
        font-weight: 900;
        margin: 0;
    }
    
    .metric-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        border: 2px solid #11998e;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .metric-value { font-size: 26px; font-weight: 900; color: #11998e; }
    .metric-label { font-size: 14px; color: #555; font-weight: 700; }
    
    .meal-title-card {
        background-color: #e8f5e9;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        color: #1b5e20;
        margin-bottom: 15px;
        border: 1px solid #c8e6c9;
    }
    </style>
""", unsafe_allow_html=True)

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- شاشة الدخول والتسجيل ---
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
            new_pass = st.text_input("اختر كلمة المرور:", type="password", key="signup_cp")
            confirm_pass = st.text_input("تأكيد كلمة المرور:", type="password", key="signup_cp2")
            
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
    # --- الواجهة الرئيسية ---
    col_h1, col_h2 = st.columns([5, 1])
    with col_h2:
        if st.button("تسجيل الخروج 🚪"):
            st.session_state["logged_in"] = False
            st.rerun()

    # العنوان الفخم النظيف
    st.markdown("""
        <div class="main-header">
            <h1>🥗 faress3rat</h1>
        </div>
    """, unsafe_allow_html=True)

    # 1. قسم حساب الاحتياج اليومي (BMR / TDEE)
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

    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    with c_m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(target_calories)}</div><div class="metric-label">سعرة مستهدفة</div></div>', unsafe_allow_html=True)
    with c_m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(protein_g)}g</div><div class="metric-label">بروتين</div></div>', unsafe_allow_html=True)
    with c_m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(carbs_g)}g</div><div class="metric-label">كربوهيدرات</div></div>', unsafe_allow_html=True)
    with c_m4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(fats_g)}g</div><div class="metric-label">دهون</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # 2. قسم تحليل الوجبة بالصورة والعداد التفاعلي
    st.subheader("📸 2. تحليل الوجبة بالذكاء الاصطناعي")
    
    st.markdown(f'<div class="meal-title-card">🍽️ الوجبة المحللة: {st.session_state["meal_name"]}</div>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state["total_cals"]}</div><div class="metric-label">سعرة حرارية</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state["total_protein"]}g</div><div class="metric-label">بروتين</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state["total_carbs"]}g</div><div class="metric-label">كربوهيدرات</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state["total_fats"]}g</div><div class="metric-label">دهون</div></div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("ارفع أو صور وجبتك هنا...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="الوجبة الملتقطة", use_container_width=True)
        
        if st.button("✨ تحليل الوجبة وتحديث العداد تلقائياً"):
            if not API_KEY:
                st.error("⚠️ لم يتم ضبط GROQ_API_KEY في Streamlit Secrets.")
            else:
                with st.spinner("جاري تحليل الوجبة بالذكاء الاصطناعي... ⚡"):
                    try:
                        client = Groq(api_key=API_KEY)
                        base64_image = encode_image(image_bytes)

                        prompt_instruction = """
                        Analyze the food in this image. Respond ONLY with a valid JSON object. Do not include markdown code block formatting like ```json.
                        The JSON must strictly follow this structure:
                        {
                            "meal_name": "اسم الوجبة بالعربي",
                            "calories": 0,
                            "protein": 0,
                            "carbs": 0,
                            "fats": 0
                        }
                        Make sure calories, protein, carbs, and fats are integer numbers only.
                        """

                        response = client.chat.completions.create(
                            model="llama-3.2-11b-vision-preview",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_instruction},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}"
                                            },
                                        },
                                    ],
                                }
                            ],
                            temperature=0.2
                        )

                        res_text = response.choices[0].message.content.strip()
                        if res_text.startswith("```"):
                            res_text = res_text.split("```")[1]
                            if res_text.startswith("json"):
                                res_text = res_text[4:]
                        res_text = res_text.strip()

                        data = json.loads(res_text)
                        
                        st.session_state["meal_name"] = data.get("meal_name", "وجبة مشكلة")
                        st.session_state["total_cals"] = int(data.get("calories", 0))
                        st.session_state["total_protein"] = int(data.get("protein", 0))
                        st.session_state["total_carbs"] = int(data.get("carbs", 0))
                        st.session_state["total_fats"] = int(data.get("fats", 0))

                        st.success("تم التحليل وتحديث العداد بنجاح! 🎉")
                        st.rerun()

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء التحليل: {e}")

    st.markdown("---")

    # 3. قسم المساعد التغذوي الذكي
    st.subheader("💬 3. المساعد التغذوي الذكي")
    user_question = st.text_input("اسأل أي سؤال تغذوي إضافي:")
    
    if user_question:
        if not API_KEY:
            st.error("⚠️ لم يتم ضبط GROQ_API_KEY في Streamlit Secrets.")
        else:
            with st.spinner("جاري الإجابة... ⚡"):
                try:
                    client = Groq(api_key=API_KEY)
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "أنت خبير تغذية محترف ومساعد ذكي. أجب باللغة العربية بدقة وبشكل مبهج ومختصر."
                            },
                            {
                                "role": "user",
                                "content": user_question,
                            }
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    st.info(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
