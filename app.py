import streamlit as st
from groq import Groq
import base64
import json

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

# 3. إدارة الجلسة
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "users_db" not in st.session_state:
    st.session_state["users_db"] = {"user": "1234"}

# قيم السعرات المأكولة
if "eaten_cals" not in st.session_state:
    st.session_state["eaten_cals"] = 0
if "eaten_protein" not in st.session_state:
    st.session_state["eaten_protein"] = 0
if "eaten_carbs" not in st.session_state:
    st.session_state["eaten_carbs"] = 0
if "eaten_fats" not in st.session_state:
    st.session_state["eaten_fats"] = 0
if "last_meal_name" not in st.session_state:
    st.session_state["last_meal_name"] = ""

# 4. التنسيق والتصميم المأخوذ بالكامل من MyFitnessPal (Dark Theme)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
        background-color: #121824 !important;
        color: #f1f5f9 !important;
        direction: rtl;
        text-align: right;
    }

    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* الهيدر العلوي */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 5px 20px 5px;
    }
    .top-header h2 {
        margin: 0;
        font-size: 28px;
        font-weight: 900;
        color: #ffffff;
    }
    
    /* شريط الأيام */
    .days-bar {
        display: flex;
        justify-content: space-between;
        background-color: #1a2232;
        padding: 12px 18px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #283448;
    }
    .day-item {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        font-weight: 700;
    }
    .day-item.active {
        color: #38ef7d;
    }
    .day-circle {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        border: 2px solid #334155;
        margin: 5px auto 0 auto;
    }
    .day-item.active .day-circle {
        border: 2px dashed #38ef7d;
        background-color: rgba(56, 239, 125, 0.1);
    }

    /* كروت MyFitnessPal */
    .mfp-card {
        background-color: #1a2232;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid #283448;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .mfp-title {
        color: #94a3b8;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .cals-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 10px;
    }

    .cals-val {
        font-size: 26px;
        font-weight: 900;
        color: #ffffff;
    }
    .cals-sub {
        font-size: 15px;
        color: #64748b;
    }
    .cals-left {
        font-size: 22px;
        font-weight: 900;
        color: #38ef7d;
    }

    .progress-bar-bg {
        background-color: #283448;
        border-radius: 8px;
        height: 8px;
        width: 100%;
        overflow: hidden;
    }

    .progress-bar-fill {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        height: 100%;
        border-radius: 8px;
    }

    /* الماكروز الثلاثة */
    .macros-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        text-align: center;
    }
    .macro-item-title {
        font-size: 13px;
        color: #94a3b8;
        font-weight: 600;
    }
    .macro-item-val {
        font-size: 18px;
        font-weight: 800;
        color: #ffffff;
        margin: 4px 0;
    }
    .macro-item-sub {
        font-size: 12px;
        color: #64748b;
    }

    /* كروت الوجبات Meals */
    .meal-card {
        background-color: #1a2232;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #283448;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .meal-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .meal-icon {
        font-size: 22px;
        background: #283448;
        padding: 8px 12px;
        border-radius: 12px;
    }
    .meal-name {
        font-size: 17px;
        font-weight: 700;
        color: #ffffff;
    }

    /* أزرار وتنسيقات الـ Streamlit */
    .stButton>button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- تسجيل الدخول ---
if not st.session_state["logged_in"]:
    st.markdown('<h1 style="text-align:center; color:#38ef7d; margin-top:30px;">🥗 faress3rat</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔐 تسجيل الدخول", "✨ حساب جديد"])
        
        with tab_login:
            login_user = st.text_input("اسم المستخدم:", key="login_u")
            login_pass = st.text_input("كلمة المرور:", type="password", key="login_p")
            if st.button("دخول 🚀", use_container_width=True):
                if login_user in st.session_state["users_db"] and st.session_state["users_db"][login_user] == login_pass:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور خطأ!")

        with tab_signup:
            new_user = st.text_input("اختر اسم المستخدم:", key="signup_u")
            new_pass = st.text_input("اختر كلمة المرور:", type="password", key="signup_p")
            confirm_pass = st.text_input("تأكيد كلمة المرور:", type="password", key="signup_cp")
            if st.button("إنشاء حساب 🎯", use_container_width=True):
                if new_user and new_pass == confirm_pass:
                    st.session_state["users_db"][new_user] = new_pass
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("تأكد من البيانات!")

else:
    # --- الواجهة الرئيسية (MyFitnessPal Style) ---
    
    # الهيدر العلوي
    c_head1, c_head2 = st.columns([4, 1])
    with c_head1:
        st.markdown('<h2 style="margin:0; color:#ffffff;">اليوم 🥗</h2>', unsafe_allow_html=True)
    with c_head2:
        if st.button("خروج 🚪"):
            st.session_state["logged_in"] = False
            st.rerun()

    # شريط الأيام العلوي
    st.markdown("""
        <div class="days-bar">
            <div class="day-item"><div style="margin-bottom:2px;">الأحد</div><div class="day-circle"></div></div>
            <div class="day-item"><div style="margin-bottom:2px;">الإثنين</div><div class="day-circle"></div></div>
            <div class="day-item"><div style="margin-bottom:2px;">الثلاثاء</div><div class="day-circle"></div></div>
            <div class="day-item active"><div style="margin-bottom:2px;">الأربعاء</div><div class="day-circle"></div></div>
            <div class="day-item"><div style="margin-bottom:2px;">الخميس</div><div class="day-circle"></div></div>
            <div class="day-item"><div style="margin-bottom:2px;">الجمعة</div><div class="day-circle"></div></div>
            <div class="day-item"><div style="margin-bottom:2px;">السبت</div><div class="day-circle"></div></div>
        </div>
    """, unsafe_allow_html=True)

    # قسم إعدادات الجسم (مخفي للترتيب)
    with st.expander("⚙️ إعدادات الهدف والطول والعمر (تعديل الاحتياج)", expanded=False):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            gender = st.radio("الجنس:", ("ذكر", "أنثى"), horizontal=True)
            age = st.number_input("العمر:", 10, 100, 25)
            weight = st.number_input("الوزن (كجم):", 30.0, 200.0, 70.0)
        with col_c2:
            height = st.number_input("الطول (سم):", 100.0, 230.0, 170.0)
            activity_level = st.selectbox("مستوى النشاط:", ["خامل (بدون تمارين)", "نشاط خفيف (1-3 أيام)", "نشاط متوسط (3-5 أيام)", "نشاط عالٍ (6-7 أيام)"])
            goal = st.selectbox("الهدف:", ["المحافظة على الوزن ⚖️", "تنشيف / إنقاص الوزن 📉", "تضخيم / زيادة الوزن 📈"])

    bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == "ذكر" else -161)
    act_map = {"خامل (بدون تمارين)": 1.2, "نشاط خفيف (1-3 أيام)": 1.375, "نشاط متوسط (3-5 أيام)": 1.55, "نشاط عالٍ (6-7 أيام)": 1.725}
    tdee = bmr * act_map[activity_level]

    target_calories = tdee - 500 if "تنشيف" in goal else (tdee + 400 if "تضخيم" in goal else tdee)
    target_protein = (target_calories * 0.30) / 4
    target_carbs = (target_calories * 0.40) / 4
    target_fats = (target_calories * 0.30) / 9

    # الحسابات المتبقية
    eaten_c = st.session_state["eaten_cals"]
    left_c = max(0, int(target_calories - eaten_c))
    cals_pct = min(100, int((eaten_c / target_calories) * 100)) if target_calories > 0 else 0

    # 1. كارت السعرات الحرارية الرئيسي (Calories Card)
    st.markdown(f"""
        <div class="mfp-card">
            <div class="mfp-title">السعرات الحرارية (Calories)</div>
            <div class="cals-row">
                <div class="cals-val">{eaten_c} <span class="cals-sub">/ {int(target_calories)}</span></div>
                <div class="cals-left">{left_c} <span style="font-size:14px; color:#64748b;">متبقي</span></div>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: {cals_pct}%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. كارت الماكروز (Carbs / Fat / Protein Card)
    e_p, t_p = st.session_state["eaten_protein"], int(target_protein)
    e_c, t_c = st.session_state["eaten_carbs"], int(target_carbs)
    e_f, t_f = st.session_state["eaten_fats"], int(target_fats)

    st.markdown(f"""
        <div class="mfp-card">
            <div class="macros-grid">
                <div>
                    <div class="macro-item-title">الكربوهيدرات</div>
                    <div class="macro-item-val">{e_c}g</div>
                    <div class="macro-item-sub">من {t_c}g</div>
                </div>
                <div>
                    <div class="macro-item-title">الدهون</div>
                    <div class="macro-item-val">{e_f}g</div>
                    <div class="macro-item-sub">من {t_f}g</div>
                </div>
                <div>
                    <div class="macro-item-title">البروتين</div>
                    <div class="macro-item-val">{e_p}g</div>
                    <div class="macro-item-sub">من {t_p}g</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3. قسم الوجبات (Meals Section)
    st.markdown('<h3 style="color:#ffffff; font-size:20px; font-weight:800; margin-top:15px;">الوجبات (Meals)</h3>', unsafe_allow_html=True)

    col_m1, col_m2 = st.columns([4, 1])
    with col_m1:
        st.markdown("""
            <div class="meal-card">
                <div class="meal-info">
                    <div class="meal-icon">☕</div>
                    <div class="meal-name">وجبة الإفطار</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.write(" ")
        st.button("+ إضافة", key="add_b", use_container_width=True)

    col_l1, col_l2 = st.columns([4, 1])
    with col_l1:
        st.markdown("""
            <div class="meal-card">
                <div class="meal-info">
                    <div class="meal-icon">🍔</div>
                    <div class="meal-name">وجبة الغداء</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col_l2:
        st.write(" ")
        st.button("+ إضافة", key="add_l", use_container_width=True)

    col_d1, col_d2 = st.columns([4, 1])
    with col_d1:
        st.markdown("""
            <div class="meal-card">
                <div class="meal-info">
                    <div class="meal-icon">🥗</div>
                    <div class="meal-name">وجبة العشاء</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col_d2:
        st.write(" ")
        st.button("+ إضافة", key="add_d", use_container_width=True)

    st.write(" ")

    # 4. قسم الكاميرا والتحليل بلمسة زر واحدة
    st.markdown('<h3 style="color:#ffffff; font-size:20px; font-weight:800;">📸 مسح وتصوير الوجبة</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("التقط صورة وجبتك لتحديث العدادات فوراً:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.button("⚡ تحليل وتسجيل الوجبة في العدادات", use_container_width=True):
            if not API_KEY:
                st.error("⚠️ يرجى التأكد من ضبط المفتاح في الإعدادات.")
            else:
                with st.spinner("جاري قراءة الوجبة وتحديث القائمة... ⚡"):
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
                        
                        st.session_state["last_meal_name"] = data.get("meal_name", "وجبة جديدة")
                        st.session_state["eaten_cals"] += int(data.get("calories", 0))
                        st.session_state["eaten_protein"] += int(data.get("protein", 0))
                        st.session_state["eaten_carbs"] += int(data.get("carbs", 0))
                        st.session_state["eaten_fats"] += int(data.get("fats", 0))

                        st.success("تم تحديث السعرات الحرارية والماكروز بنجاح! 🎉")
                        st.rerun()

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء القراءة: {e}")

    # 5. المساعد التغذوي
    with st.expander("💬 المساعد التغذوي المباشر", expanded=False):
        user_question = st.text_input("اسأل المساعد عن أي استفسار تغذوي:")
        if user_question and API_KEY:
            with st.spinner("جاري الإجابة... ⚡"):
                try:
                    client = Groq(api_key=API_KEY)
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "أنت خبير تغذية ومساعد محترف. أجب باللغة العربية بدقة وبشكل مختصر."},
                            {"role": "user", "content": user_question}
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    st.info(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
