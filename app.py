import streamlit as st
from google import genai
from PIL import Image

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="FitAI | حاسبة وتتبع السعرات الذكية",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. إضافة CSS لتجميل وتحسين مظهر الموقع بالكامل
st.markdown("""
    <style>
    /* تحسين الخط والخلفية العامة */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    /* تصميم الهيدر الرئيسي */
    .main-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white !important;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    /* بطاقات الماكروز والسعرات */
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #11998e;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
    }
    
    /* تحسين زر التفاعل */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 12px;
        border: none;
        font-size: 18px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: scale(1.01);
    }
    </style>
""", unsafe_allow_html=True)

# 3. الهيدر الرئيسي للموقع
st.markdown("""
    <div class="main-header">
        <h1>🥗 FitAI — رفيقك التغذوي الذكي</h1>
        <p>احسب احتياجك اليومي، صور وجبتك بالذكاء الاصطناعي، وتتبع سعراتك بكل سهولة!</p>
    </div>
""", unsafe_allow_html=True)

# 4. القائمة الجانبية (Sidebar) للـ API Key وإعدادات الحساب
with st.sidebar:
    st.header("⚙️ الإعدادات والمفتاح")
    api_key = st.text_input("أدخل Gemini API Key:", type="password", help="احصل عليه مجاناً من Google AI Studio")
    st.markdown("---")
    st.info("💡 **تلميح:** يمكنك حفظ مفتاح الـ API للوصول السريع ومباشرة تحليل صور الوجبات.")

# 5. قسم حساب الاحتياج اليومي (BMR & TDEE Calculator)
st.subheader("📊 1. حساب الاحتياج اليومي من السعرات (TDEE)")

col_calc1, col_calc2 = st.columns([1, 1])

with col_calc1:
    gender = st.radio("الجنس:", ("ذكر", "أنثى"), horizontal=True)
    age = st.number_input("العمر (سنة):", min_value=10, max_value=100, value=25)
    weight = st.number_input("الوزن (كجم):", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
    height = st.number_input("الطول (سم):", min_value=100.0, max_value=230.0, value=170.0, step=1.0)

with col_calc2:
    activity_level = st.selectbox(
        "مستوى النشاط اليومي:",
        [
            "خامل (مكتب/بدون تمارين)",
            "نشاط خفيف (تمارين 1-3 أيام بالأسبوع)",
            "نشاط متوسط (تمارين 3-5 أيام بالأسبوع)",
            "نشاط عالٍ (تمارين 6-7 أيام بالأسبوع)",
            "نشاط فائق (تمارين شاقة يومياً/عمل بدني)"
        ]
    )
    
    goal = st.selectbox(
        "الهدف الصحي:",
        ["المحافظة على الوزن ⚖️", "إنقاص الوزن (تنشيف) 📉", "زيادة الوزن (تضخيم) 📈"]
    )

# معادلة حساب BMR (Mifflin-St Jeor)
if gender == "ذكر":
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
else:
    bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

# معامل النشاط
activity_multipliers = {
    "خامل (مكتب/بدون تمارين)": 1.2,
    "نشاط خفيف (تمارين 1-3 أيام بالأسبوع)": 1.375,
    "نشاط متوسط (تمارين 3-5 أيام بالأسبوع)": 1.55,
    "نشاط عالٍ (تمارين 6-7 أيام بالأسبوع)": 1.725,
    "نشاط فائق (تمارين شاقة يومياً/عمل بدني)": 1.9
}

tdee = bmr * activity_multipliers[activity_level]

# تعديل السعرات حسب الهدف
if goal == "إنقاص الوزن (تنشيف) 📉":
    target_calories = tdee - 500
elif goal == "زيادة الوزن (تضخيم) 📈":
    target_calories = tdee + 400
else:
    target_calories = tdee

# حساب الماكروز التقديرية
protein_g = (target_calories * 0.30) / 4
carbs_g = (target_calories * 0.40) / 4
fats_g = (target_calories * 0.30) / 9

# عرض نتائج العداد بشكل أنيق
st.markdown("#### 🎯 احتياجك اليومي الموصى به:")
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{int(target_calories)}</div><div class="metric-label">سعرة حرارية / يوم</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{int(protein_g)}g</div><div class="metric-label">بروتين</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{int(carbs_g)}g</div><div class="metric-label">كربوهيدرات</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{int(fats_g)}g</div><div class="metric-label">دهون</div></div>', unsafe_allow_html=True)

st.markdown("---")

# 6. قسم تحليل الوجبة بالذكاء الاصطناعي
st.subheader("📸 2. تحليل الوجبة بالذكاء الاصطناعي")

if not api_key:
    st.warning("⚠️ يرجى إدخال Gemini API Key في القائمة الجانبية لبدء استخدام تحليل الصور بالشات.")
else:
    client = genai.Client(api_key=api_key)

    col_img1, col_img2 = st.columns([1, 1])

    with col_img1:
        source_option = st.radio("طريقة التقاط/رفع الصورة:", ("التقاط صورة بالكاميرا 📷", "رفع صورة من الجهاز 📁"), horizontal=True)
        
        uploaded_file = None
        if source_option == "التقاط صورة بالكاميرا 📷":
            uploaded_file = st.camera_input("التقط صورة وجبتك")
        else:
            uploaded_file = st.file_uploader("اختر صورة الوجبة من جهازك...", type=["jpg", "jpeg", "png"])

    with col_img2:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="الوجبة المراد تحليلها", use_container_width=True)
            
            analyze_btn = st.button("✨ تحليل الوجبة وحساب السعرات")
            
            if analyze_btn:
                with st.spinner("جاري التعرف على العناصر الغذائية وحساب السعرات... ⏳"):
                    prompt = f"""
                    أنت أخصائي تغذية خبير ومحترف. قم بتحليل صورة الوجبة التالية بدقة باللغة العربية:
                    
                    السياق: المستخدم يحتاج {int(target_calories)} سعرة حرارية يومياً لهدفه ({goal}).
                    
                    قم بإخراج النتيجة بالتنسيق التالي بدقة:
                    1. 🍽️ **اسم الوجبة ومكوناتها:** (حدد المكونات بالتفصيل وتقدير أوزانها).
                    2. 📊 **القيمة الغذائية التقريبية:**
                       - السعرات الحرارية الإجمالية:
                       - البروتين (غرام):
                       - الكربوهيدرات (غرام):
                       - الدهون (غرام):
                    3. 💡 **تقييم الوجبة ونصيحة صحية:** (هل تناسب هدفه؟ وما هي الاقتراحات لتحسينها؟).
                    
                    استخدم تنسيق Markdown واجعل الشكل منسقاً ومنظماً جداً.
                    """
                    
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[prompt, image]
                        )
                        st.success("تم تحليل الوجبة بنجاح! 🎉")
                        st.markdown("---")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")

st.markdown("---")

# 7. المساعد الذكي للإجابة عن الأسئلة
st.subheader("💬 3. المساعد التغذوي الذكي")

user_question = st.text_input("هل لديك أي سؤال عن التغذية أو خيارات بديلة لوجبتك؟")
if user_question:
    if not api_key:
        st.error("يرجى إدخال API Key أولاً في القائمة الجانبية.")
    else:
        with st.spinner("جاري الرد عليك..."):
            try:
                chat_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"أجب عن سؤال المستخدم كأخصائي تغذية مشجع ومحترف باللغة العربية: {user_question}"
                )
                st.info(chat_response.text)
            except Exception as e:
                st.error(f"حدث خطأ: {e}")