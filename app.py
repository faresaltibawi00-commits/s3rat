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

# 2. جلب المفتاح
API_KEY = None
if "GROQ_API_KEY" in st.secrets:
    API_KEY = str(st.secrets["GROQ_API_KEY"]).strip()

# 3. إدارة جلسة المستخدم
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "users_db" not in st.session_state:
    st.session_state["users_db"] = {"user": "1234"}

# العدادات الفورية
if "total_cals" not in st.session_state:
    st.session_state["total_cals"] = 0
if "total_protein" not in st.session_state:
    st.session_state["total_protein"] = 0
if "total_carbs" not in st.session_state:
    st.session_state["total_carbs"] = 0
if "total_fats" not in st.session_state:
    st.session_state["total_fats"] = 0
if "meal_name" not in st.session_state:
    st.session_state["meal_name"] = "لم يتم تحديد وجبة بعد"

# 4. تصميم فاخر وعصري (Modern Dark Glassmorphism)
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

    /* الهيدر والعنوان الرئيسي */
    .brand-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(17, 153, 142, 0.25);
    }
    .brand-header h1 {
        font-size: 42px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 1px;
        color: #ffffff !important;
    }
    .brand-header p {
        font-size: 16px;
        margin-top: 8px;
        opacity: 0.95;
    }

    /* كروت العدادات الفخمة */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: 4px solid #38ef7d;
        border-radius: 16px;
        padding: 20px 10px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }
    .metric-value {
        font-size: 30px;
        font-weight: 900;
        color: #38ef7d;
    }
    .metric-label {
        font-size: 14px;
        color: #a0aec0;
        font-weight: 700;
        margin-top: 4px;
    }

    /* عنوان الوجبة */
    .meal-box {
        background: rgba(56, 239, 125, 0.1);
        border: 1px dashed #38ef7d;
        border-radius: 14px;
        padding: 14px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: #38ef7d;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- تسجيل الدخول / إنشاء حساب ---
if not st.session_state["logged_in"]:
    st.markdown("""
        <div class="brand-header">
            <h1>🥗 faress3rat</h1>
            <p>منصتك الاحترافية لإدارة التغذية والحسابات الرياضية</p>
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
    # --- الواجهة الرئيسية ---
    col_h1, col_h2 = st.columns([5, 1])
    with col_h2:
        if st.button("تسجيل الخروج 🚪"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.markdown("""
        <div class="brand-header">
            <h1>🥗 faress3rat</h1>
        </div>
    """, unsafe_allow_html=True)

    # 1. قسم حساب الاحتياج اليومي
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

    # 2. قسم التحليل بالصور والعدادات
    st.subheader("📸 2. تحليل الوجبة تلقائياً")
    
    st.markdown(f'<div class="meal-box">🍽️ الوجبة الحالية: {st.session_state["meal_name"]}</div>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state["total_cals"]}</div><div class="metric-label">سعرة حرارية</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state["total_protein"]}g</div><div class="metric-label">بروتين</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state["total_carbs"]}g</div><div class="metric-label">كربوهيدرات</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state["total_fats"]}g</div><div class="metric-label">دهون</div></div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("التقط أو ارفع صورة الوجبة:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.button("⚡ تحليل الوجبة واستخراج القيم"):
            if not API_KEY:
                st.error("⚠️ يرجى التأكد من ضبط المفتاح في الإعدادات.")
            else:
                with st.spinner("جاري قراءة تفاصيل الوجبة وحساب القيم... ⚡"):
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

                        st.success("تم تحديث العدادات بنجاح! 🎉")
                        st.rerun()

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء القراءة: {e}")

    st.markdown("---")

    # 3. قسم المساعد التغذوي
    st.subheader("💬 3. المساعد التغذوي المباشر")
    user_question = st.text_input("اطرح أي سؤال تغذوي:")
    
    if user_question:
        if not API_KEY:
            st.error("⚠️ يرجى التأكد من ضبط المفتاح في الإعدادات.")
        else:
            with st.spinner("جاري الإجابة... ⚡"):
                try:
                    client = Groq(api_key=API_KEY)
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "أنت خبير تغذية ومساعد محترف. أجب باللغة العربية بدقة وبشكل مبهج ومختصر."
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
