import streamlit as st
from groq import Groq
import base64
import json
import io
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

# 3. إدارة جلسة المستخدم والبيانات المتغيرة
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "users_db" not in st.session_state:
    st.session_state["users_db"] = {"user": "1234"}

# العدادات التفاعلية للوجبة المحللة
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

# 4. التنسيق والتصميم
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
        border: 2px solid #38ef7d;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #11998e; }
    .metric-label { font-size: 14px; color: #6c757d; font-weight: bold; }
    .meal-title-card {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        color: #2e7d32;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# دالة تحويل الصورة إلى Base64
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- شاشة تسجيل الدخول وإنشاء الحساب ---
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
    # --- الواجهة الرئيسية للبرنامج ---
    col_h1, col_h2 = st.columns([5, 1])
    with col_h2:
        if st.button("تسجيل الخروج 🚪"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.markdown("""
        <div class="main-header">
            <h1>🥗 faress3rat</h1>
            <p>عداد السعرات التلقائي بالذكاء الاصطناعي</p>
        </div>
    """, unsafe_allow_html=True)

    # 📌 العدادات العلويّة التي تُحَدّث تلقائياً عند تحليل الصورة
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

    st.markdown("---")

    # 2. قسم التصوير / رفع الصورة وتحليلها آلياً
    st.subheader("📸 1. صور وجبتك لتحليلها فورياً")

    uploaded_file = st.file_uploader("ارفع أو صور وجبتك هنا...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="الوجبة الملتقطة", use_container_width=True)
        
        if st.button("✨ تحليل الوجبة وتحديث العداد تلقائياً"):
            if not API_KEY:
                st.error("⚠️ لم يتم ضبط GROQ_API_KEY في Streamlit Secrets.")
            else:
                with st.spinner("جاري تحليل الوجبة بالذكاء الاصطناعي وتحديث العداد فوق... ⚡"):
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
                        # تنظيف النص إذا أرجع الموديل أقواس كود
                        if res_text.startswith("```"):
                            res_text = res_text.split("```")[1]
                            if res_text.startswith("json"):
                                res_text = res_text[4:]
                        res_text = res_text.strip()

                        # تحويل النتيجة لـ JSON وتحديث العدادات فوق
                        data = json.loads(res_text)
                        
                        st.session_state["meal_name"] = data.get("meal_name", "وجبة مشكلة")
                        st.session_state["total_cals"] = int(data.get("calories", 0))
                        st.session_state["total_protein"] = int(data.get("protein", 0))
                        st.session_state["total_carbs"] = int(data.get("carbs", 0))
                        st.session_state["total_fats"] = int(data.get("fats", 0))

                        st.success("تم التحليل وتحديث العداد فوق بنجاح! 🎉")
                        st.rerun()

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء التحليل: {e}")

    st.markdown("---")

    # 3. قسم المساعد التغذوي الذكي
    st.subheader("💬 2. المساعد التغذوي الذكي")
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
