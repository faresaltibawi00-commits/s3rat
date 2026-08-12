import streamlit as st
from groq import Groq
import base64
import json
import os

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

# 3. إدارة قاعدة البيانات المحلية
DB_FILE = "users_db.json"

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users_data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

users_db = load_users()

# 4. إدارة الجلسة الحالية
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "active_meal_type" not in st.session_state:
    st.session_state["active_meal_type"] = None

# 5. التنسيق والتصميم (MyFitnessPal Style)
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
    .day-item.active { color: #38ef7d; }
    .day-circle {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        border: 2px solid #334155;
        margin: 5px auto 0 auto;
    }
    .day-item.active .day-circle {
        border: 2px dashed #38ef7d;
        background-color: rgba(56, 239, 125, 0.1);
    }

    .mfp-card {
        background-color: #1a2232;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid #283448;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .mfp-title { color: #94a3b8; font-size: 15px; font-weight: 700; margin-bottom: 12px; }
    .cals-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
    .cals-val { font-size: 26px; font-weight: 900; color: #ffffff; }
    .cals-sub { font-size: 15px; color: #64748b; }
    .cals-left { font-size: 22px; font-weight: 900; color: #38ef7d; }

    .progress-bar-bg { background-color: #283448; border-radius: 8px; height: 8px; width: 100%; overflow: hidden; }
    .progress-bar-fill { background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); height: 100%; border-radius: 8px; }

    .macros-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align: center; }
    .macro-item-title { font-size: 13px; color: #94a3b8; font-weight: 600; }
    .macro-item-val { font-size: 18px; font-weight: 800; color: #ffffff; margin: 4px 0; }
    .macro-item-sub { font-size: 12px; color: #64748b; }

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
    .meal-info { display: flex; align-items: center; gap: 12px; }
    .meal-icon { font-size: 22px; background: #283448; padding: 8px 12px; border-radius: 12px; }
    .meal-name { font-size: 17px; font-weight: 700; color: #ffffff; }

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

# --- 1. شاشة تسجيل الدخول وإنشاء الحساب ---
if not st.session_state["logged_in"]:
    st.markdown('<h1 style="text-align:center; color:#38ef7d; margin-top:30px; font-weight:900;">🥗 faress3rat</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔐 تسجيل الدخول", "✨ حساب جديد"])
        
        with tab_login:
            login_user = st.text_input("اسم المستخدم:", key="login_u").strip()
            login_pass = st.text_input("كلمة المرور:", type="password", key="login_p").strip()
            if st.button("دخول 🚀", use_container_width=True):
                if login_user in users_db and users_db[login_user]["pass"] == login_pass:
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = login_user
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")

        with tab_signup:
            new_user = st.text_input("اختر اسم المستخدم:", key="signup_u").strip()
            new_pass = st.text_input("اختر كلمة المرور:", type="password", key="signup_p").strip()
            confirm_pass = st.text_input("تأكيد كلمة المرور:", type="password", key="signup_cp").strip()
            if st.button("إنشاء حساب 🎯", use_container_width=True):
                if not new_user or not new_pass:
                    st.warning("يرجى ملء جميع الحقول!")
                elif new_user in users_db:
                    st.error("اسم المستخدم هذا مسجل بالفعل!")
                elif new_pass != confirm_pass:
                    st.error("كلمتا المرور غير متطابقتين!")
                else:
                    users_db[new_user] = {
                        "pass": new_pass,
                        "profile": None,
                        "eaten": {"cals": 0, "protein": 0, "carbs": 0, "fats": 0}
                    }
                    save_users(users_db)
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = new_user
                    st.success("تم إنشاء الحساب بنجاح!")
                    st.rerun()

else:
    user_key = st.session_state["current_user"]
    user_data = users_db.get(user_key, {})
    user_profile = user_data.get("profile")

    # تهيئة بيانات الأكل المحفوظة
    if "eaten" not in user_data:
        user_data["eaten"] = {"cals": 0, "protein": 0, "carbs": 0, "fats": 0}

    # --- 2. شاشة إدخال الجسم والهدف ---
    if not user_profile:
        st.markdown('<h2 style="text-align:center; color:#38ef7d;">📝 البيانات الشخصية والهدف</h2>', unsafe_allow_html=True)
        st.write("أهلاً بك! يرجى إدخال بياناتك بدقة لتحديد الاحتياج اليومي المناسب لك:")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            gender = st.radio("الجنس:", ("ذكر", "أنثى"), horizontal=True)
            age = st.number_input("العمر (سنة):", min_value=12, max_value=90, value=20)
            weight = st.number_input("الوزن الحالي (كجم):", min_value=30.0, max_value=200.0, value=70.0)
        with col_p2:
            height = st.number_input("الطول (سم):", min_value=100.0, max_value=230.0, value=170.0)
            activity_level = st.selectbox("مستوى النشاط البدني:", [
                "خامل (مكتب، بدون تمارين)",
                "نشاط خفيف (تمارين 1-3 أيام/أسبوع)",
                "نشاط متوسط (تمارين 3-5 أيام/أسبوع)",
                "نشاط عالٍ (تمارين 6-7 أيام/أسبوع)"
            ])
            goal = st.selectbox("هدف الاستهداف:", [
                "المحافظة على الوزن الحالي ⚖️",
                "تنشيف / خصر وإنقاص الدهون 📉",
                "تضخيم / زيادة الكتلة العضلية 📈"
            ])

        if st.button("حفظ البيانات والدخول للبرنامج 🚀", use_container_width=True):
            if gender == "ذكر":
                bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
            else:
                bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

            act_factors = {
                "خامل (مكتب، بدون تمارين)": 1.2,
                "نشاط خفيف (تمارين 1-3 أيام/أسبوع)": 1.375,
                "نشاط متوسط (تمارين 3-5 أيام/أسبوع)": 1.55,
                "نشاط عالٍ (تمارين 6-7 أيام/أسبوع)": 1.725
            }
            tdee = bmr * act_factors[activity_level]

            if "تنشيف" in goal:
                target_cals = tdee - 500
            elif "تضخيم" in goal:
                target_cals = tdee + 350
            else:
                target_cals = tdee

            target_p = weight * 2.0
            target_f = weight * 0.9
            rem_cals_for_carbs = target_cals - ((target_p * 4) + (target_f * 9))
            target_c = max(50, rem_cals_for_carbs / 4)

            users_db[user_key]["profile"] = {
                "gender": gender, "age": age, "weight": weight, "height": height,
                "activity": activity_level, "goal": goal,
                "target_cals": int(target_cals),
                "target_p": int(target_p),
                "target_c": int(target_c),
                "target_f": int(target_f)
            }
            save_users(users_db)
            st.rerun()

    # --- 3. الواجهة الرئيسية للبرنامج ---
    else:
        prof = user_profile
        eaten_data = user_data["eaten"]
        
        c_head1, c_head2 = st.columns([4, 1])
        with c_head1:
            st.markdown(f'<h2 style="margin:0; color:#ffffff;">أهلاً {user_key} 🥗</h2>', unsafe_allow_html=True)
        with c_head2:
            if st.button("خروج 🚪"):
                st.session_state["logged_in"] = False
                st.session_state["current_user"] = None
                st.rerun()

        # شريط الأيام
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

        # زر تعديل البيانات وتصفير اليوم
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            if st.button("🔄 إعادة ضبط البيانات الشخصية"):
                users_db[user_key]["profile"] = None
                save_users(users_db)
                st.rerun()
        with col_opt2:
            if st.button("🗑️ تصفير سعرات اليوم"):
                users_db[user_key]["eaten"] = {"cals": 0, "protein": 0, "carbs": 0, "fats": 0}
                save_users(users_db)
                st.rerun()

        # الحسابات
        target_cals = prof["target_cals"]
        eaten_c = eaten_data["cals"]
        left_c = max(0, target_cals - eaten_c)
        cals_pct = min(100, int((eaten_c / target_cals) * 100)) if target_cals > 0 else 0

        # كارت السعرات الحرارية
        st.markdown(f"""
            <div class="mfp-card">
                <div class="mfp-title">السعرات الحرارية اليومية</div>
                <div class="cals-row">
                    <div class="cals-val">{eaten_c} <span class="cals-sub">/ {target_cals}</span></div>
                    <div class="cals-left">{left_c} <span style="font-size:14px; color:#64748b;">متبقي</span></div>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: {cals_pct}%;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # كارت الماكروز
        st.markdown(f"""
            <div class="mfp-card">
                <div class="macros-grid">
                    <div>
                        <div class="macro-item-title">الكربوهيدرات</div>
                        <div class="macro-item-val">{eaten_data["carbs"]}g</div>
                        <div class="macro-item-sub">من {prof["target_c"]}g</div>
                    </div>
                    <div>
                        <div class="macro-item-title">الدهون</div>
                        <div class="macro-item-val">{eaten_data["fats"]}g</div>
                        <div class="macro-item-sub">من {prof["target_f"]}g</div>
                    </div>
                    <div>
                        <div class="macro-item-title">البروتين</div>
                        <div class="macro-item-val">{eaten_data["protein"]}g</div>
                        <div class="macro-item-sub">من {prof["target_p"]}g</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- 4. قائمة الوجبات والإضافة اليدوية ---
        st.markdown('<h3 style="color:#ffffff; font-size:20px; font-weight:800; margin-top:15px;">الوجبات (Meals)</h3>', unsafe_allow_html=True)

        meals_list = [("☕", "وجبة الإفطار"), ("🍔", "وجبة الغداء"), ("🥗", "وجبة العشاء")]
        for m_icon, m_name in meals_list:
            col_m1, col_m2 = st.columns([4, 1])
            with col_m1:
                st.markdown(f"""
                    <div class="meal-card">
                        <div class="meal-info">
                            <div class="meal-icon">{m_icon}</div>
                            <div class="meal-name">{m_name}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.write(" ")
                if st.button(f"+ إضافة", key=f"btn_{m_name}", use_container_width=True):
                    st.session_state["active_meal_type"] = m_name

        # نموذج إضافة وجبة يدوي عند ضغط زر "+ إضافة"
        if st.session_state["active_meal_type"]:
            meal_type = st.session_state["active_meal_type"]
            with st.form(key="add_meal_form"):
                st.markdown(f'<h4 style="color:#38ef7d;">إضافة عنصر إلى: {meal_type}</h4>', unsafe_allow_html=True)
                m_cals = st.number_input("السعرات الحرارية (kcal):", min_value=0, value=250)
                m_prot = st.number_input("البروتين (جرام):", min_value=0, value=20)
                m_carb = st.number_input("الكربوهيدرات (جرام):", min_value=0, value=30)
                m_fats = st.number_input("الدهون (جرام):", min_value=0, value=5)
                
                btn_submit = st.form_submit_button("إضافة الوجبة للعدادات 🎯")
                if btn_submit:
                    users_db[user_key]["eaten"]["cals"] += m_cals
                    users_db[user_key]["eaten"]["protein"] += m_prot
                    users_db[user_key]["eaten"]["carbs"] += m_carb
                    users_db[user_key]["eaten"]["fats"] += m_fats
                    save_users(users_db)
                    st.session_state["active_meal_type"] = None
                    st.success(f"تمت إضافة الوجبة إلى {meal_type}!")
                    st.rerun()

        # --- 5. ماسح الوجبة بالذكاء الاصطناعي (بالصورة) ---
        st.markdown('<h3 style="color:#ffffff; font-size:20px; font-weight:800; margin-top:20px;">📸 مسح وتصوير الوجبة بالذكاء الاصطناعي</h3>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("التقط صورة الوجبة لتحديث العداد تلقائياً:", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            image_bytes = uploaded_file.read()
            st.image(image_bytes, caption="الوجبة المرفوعة", use_container_width=True)
            
            if st.button("⚡ تحليل وتسجيل الوجبة بالصورة", use_container_width=True):
                if not API_KEY:
                    st.error("⚠️ يرجى ضبط GROQ_API_KEY في Secrets.")
                else:
                    with st.spinner("جاري تحليل الوجبة... ⚡"):
                        try:
                            client = Groq(api_key=API_KEY)
                            base64_image = encode_image(image_bytes)

                            prompt_instruction = """
                            Analyze the food in this image. Respond ONLY with a valid JSON object.
                            Structure:
                            {
                                "meal_name": "اسم الوجبة بالعربي",
                                "calories": 0,
                                "protein": 0,
                                "carbs": 0,
                                "fats": 0
                            }
                            Use integer numbers for values.
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
                                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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
                            
                            users_db[user_key]["eaten"]["cals"] += int(data.get("calories", 0))
                            users_db[user_key]["eaten"]["protein"] += int(data.get("protein", 0))
                            users_db[user_key]["eaten"]["carbs"] += int(data.get("carbs", 0))
                            users_db[user_key]["eaten"]["fats"] += int(data.get("fats", 0))
                            save_users(users_db)

                            st.success(f"تم تسجيل {data.get('meal_name', 'الوجبة')} بنجاح! 🎉")
                            st.rerun()

                        except Exception as e:
                            st.error(f"حدث خطأ أثناء قراءة الصورة: {e}")

        # --- 6. المساعد التغذوي الذكي المباشر ---
        st.markdown('<h3 style="color:#ffffff; font-size:20px; font-weight:800; margin-top:25px;">💬 المساعد التغذوي الذكي</h3>', unsafe_allow_html=True)
        with st.expander("اسأل أخصائي التغذية الذكي عن أي استفسار", expanded=True):
            user_question = st.text_input("مثال: كم سعرة في بيضتين مسلوقتين؟ أو اقترح لي وجبة عشاء عالية بالبروتين:")
            if st.button("إرسال السؤال 🤖") and user_question:
                if not API_KEY:
                    st.error("⚠️ يرجى التأكد من ضبط مفتاح GROQ_API_KEY.")
                else:
                    with st.spinner("جاري التفكير والتأكد من المعلومة... ⚡"):
                        try:
                            client = Groq(api_key=API_KEY)
                            chat_completion = client.chat.completions.create(
                                messages=[
                                    {"role": "system", "content": "أنت أخصائي تغذية وخبير دايت محترف ومبتكر. أجب باللغة العربية بدقة عالية وبأسلوب مشجع ومختصر."},
                                    {"role": "user", "content": user_question}
                                ],
                                model="llama-3.3-70b-versatile",
                            )
                            st.info(chat_completion.choices[0].message.content)
                        except Exception as e:
                            st.error(f"حدث خطأ: {e}")
