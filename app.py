import locale
import os

# ضبط الترميز للعربية
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    pass
import streamlit as st
import pandas as pd
import numpy as np
import os
from utils.data_processor import DataProcessor
from utils.chart_generator import ChartGenerator  
from utils.report_generator import ReportGenerator
from utils.auth_handler import AuthHandler

# إعداد الصفحة مع دعم RTL
st.set_page_config(
    page_title="منصة تحليل درجات الطلاب",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS لدعم RTL
st.markdown("""
<style>
    .main .block-container {
        direction: rtl;
        text-align: right;
    }
    .stSelectbox label, .stFileUploader label, .stTextInput label {
        direction: rtl;
        text-align: right;
    }
    .stDataFrame {
        direction: ltr;
    }
    h1, h2, h3 {
        text-align: right;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # التحقق من المصادقة
    auth_handler = AuthHandler()
    
    if not auth_handler.is_authenticated():
        st.title("🔐 تسجيل الدخول")
        st.info("يرجى تسجيل الدخول للوصول إلى منصة تحليل الدرجات")
        
        if st.button("تسجيل الدخول باستخدام Replit"):
            auth_handler.login()
            st.rerun()
        return
    
    # العنوان الرئيسي
    st.title("📊 منصة تحليل درجات الطلاب")
    st.markdown("---")
    
    # الشريط الجانبي
    with st.sidebar:
        st.header("🎯 القائمة الرئيسية")
        st.write(f"مرحباً، {auth_handler.get_user_info().get('name', 'المستخدم')}")
        
        if st.button("تسجيل الخروج"):
            auth_handler.logout()
            st.rerun()
        
        st.markdown("---")
        st.info("💡 **نصائح الاستخدام:**\n\n"
                "• تأكد من أن ملف Excel يحتوي على أعمدة: اسم الطالب، الدرجة\n"
                "• الدرجات يجب أن تكون رقمية\n"
                "• يمكن رفع ملفات .xlsx و .xls")
    
    # تهيئة معالج البيانات
    data_processor = DataProcessor()
    chart_generator = ChartGenerator()
    report_generator = ReportGenerator()
    
    # قسم رفع الملف
    st.header("📁 رفع ملف البيانات")
    
    # أزرار تحميل الملفات التجريبية
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col2:
        if st.button("📥 نموذج بسيط", type="secondary", help="ملف يحتوي على اسم الطالب والدرجة فقط"):
            try:
                with open("sample_grades.xlsx", "rb") as file:
                    st.download_button(
                        label="⬇️ تحميل النموذج البسيط",
                        data=file.read(),
                        file_name="نموذج_بسيط.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except FileNotFoundError:
                st.error("الملف غير موجود")
    
    with col3:
        if st.button("📋 نموذج شامل", type="secondary", help="ملف يحتوي على بيانات كاملة: اسم الطالب، الدرجة، المعلم، المدير، الصف، إلخ"):
            try:
                with open("نموذج_درجات_شامل.xlsx", "rb") as file:
                    st.download_button(
                        label="⬇️ تحميل النموذج الشامل",
                        data=file.read(),
                        file_name="نموذج_درجات_شامل.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except FileNotFoundError:
                st.error("الملف غير موجود")
    
    with col4:
        if st.button("🎯 النموذج المطلوب", type="primary", help="النموذج حسب التصميم المحدد: اسم الطالب، الصف، الفصل، الدرجة، المادة، الدرجة الكلية، المعلم، المدير"):
            try:
                with open("نموذج_درجات_مخصص.xlsx", "rb") as file:
                    st.download_button(
                        label="⬇️ تحميل النموذج المطلوب",
                        data=file.read(),
                        file_name="نموذج_درجات_مخصص.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except FileNotFoundError:
                st.error("الملف غير موجود")
    
    with col1:
        uploaded_file = st.file_uploader(
            "اختر ملف Excel يحتوي على درجات الطلاب",
            type=['xlsx', 'xls'],
            help="يجب أن يحتوي الملف على عمودين على الأقل: اسم الطالب والدرجة"
        )
    
    if uploaded_file is not None:
        try:
            # قراءة البيانات
            with st.spinner("جاري تحليل البيانات..."):
                df = data_processor.load_excel_file(uploaded_file)
                
                if df is not None and not df.empty:
                    st.success("✅ تم تحميل البيانات بنجاح!")
                    
                    # عرض معاينة البيانات
                    st.subheader("📋 معاينة البيانات")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # الإحصائيات الأساسية
                    st.subheader("📈 الإحصائيات الأساسية")
                    stats = data_processor.calculate_basic_stats(df)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("عدد الطلاب", stats['count'])
                    with col2:
                        if 'النسبة المئوية' in df.columns:
                            st.metric("متوسط النسبة المئوية", f"{stats.get('percentage_mean', 0):.1f}%")
                        else:
                            st.metric("المتوسط", f"{stats['mean']:.2f}")
                    with col3:
                        st.metric("أعلى درجة", stats['max'])
                    with col4:
                        st.metric("أقل درجة", stats['min'])
                    
                    col5, col6, col7, col8 = st.columns(4)
                    with col5:
                        st.metric("الوسيط", f"{stats['median']:.2f}")
                    with col6:
                        if 'الدرجة الكلية' in df.columns:
                            st.metric("متوسط الدرجة الكلية", f"{stats.get('total_mean', 0):.2f}")
                        else:
                            st.metric("الانحراف المعياري", f"{stats['std']:.2f}")
                    with col7:
                        st.metric("النجاح (%)", f"{stats['pass_rate']:.1f}%")
                    with col8:
                        st.metric("الرسوب (%)", f"{stats['fail_rate']:.1f}%")
                    
                    st.markdown("---")
                    
                    # التحليل التفصيلي
                    st.subheader("📊 التحليل التفصيلي")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # مخطط توزيع الدرجات
                        hist_fig = chart_generator.create_histogram(df)
                        st.plotly_chart(hist_fig, use_container_width=True)
                        
                        # مخطط دائري للنجاح والرسوب
                        pie_fig = chart_generator.create_pie_chart(stats)
                        st.plotly_chart(pie_fig, use_container_width=True)
                    
                    with col2:
                        # مخطط الدرجات حسب النطاق
                        grade_ranges = data_processor.categorize_grades(df)
                        bar_fig = chart_generator.create_bar_chart(grade_ranges)
                        st.plotly_chart(bar_fig, use_container_width=True)
                        
                        # مخطط صندوقي
                        box_fig = chart_generator.create_box_plot(df)
                        st.plotly_chart(box_fig, use_container_width=True)
                    
                    # جدول التفاصيل حسب النطاق
                    st.subheader("📋 تفاصيل الدرجات حسب النطاق")
                    grade_details = data_processor.get_grade_details(df)
                    st.dataframe(grade_details, use_container_width=True)
                    
                    # قسم التقارير
                    st.markdown("---")
                    st.subheader("📄 تحميل التقارير")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("📊 تقرير Excel", type="primary"):
                            with st.spinner("جاري إنتاج التقرير..."):
                                try:
                                    report_file = report_generator.generate_comprehensive_report(df, stats, grade_ranges)
                                    with open(report_file, "rb") as file:
                                        excel_data = file.read()
                                    os.unlink(report_file)
                                    
                                    st.download_button(
                                        label="⬇️ تحميل التقرير الشامل (Excel)",
                                        data=excel_data,
                                        file_name=f"تقرير_الدرجات_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                                except Exception as e:
                                    st.error(f"خطأ في إنتاج التقرير: {str(e)}")
                    
                    with col2:
                        if st.button("📄 تقرير PDF", type="secondary"):
                            with st.spinner("جاري إنتاج التقرير..."):
                                try:
                                    pdf_file = report_generator.generate_pdf_report(df, stats, grade_ranges)
                                    with open(pdf_file, "rb") as file:
                                        pdf_data = file.read()
                                    os.unlink(pdf_file)
                                    
                                    st.download_button(
                                        label="⬇️ تحميل التقرير الشامل (PDF)",
                                        data=pdf_data,
                                        file_name=f"تقرير_الدرجات_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf"
                                    )
                                except Exception as e:
                                    st.error(f"خطأ في إنتاج التقرير: {str(e)}")
                    
                    with col3:
                        if st.button("👑 قائمة المتفوقين"):
                            top_students = data_processor.get_top_students(df, top_n=10)
                            csv = top_students.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="⬇️ تحميل قائمة المتفوقين",
                                data=csv,
                                file_name=f"الطلاب_المتفوقين_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    
                    with col4:
                        if st.button("📉 قائمة المتعثرين"):
                            failing_students = data_processor.get_failing_students(df)
                            csv = failing_students.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="⬇️ تحميل قائمة المتعثرين",
                                data=csv,
                                file_name=f"الطلاب_المتعثرين_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    
                else:
                    st.error("❌ لا يمكن قراءة البيانات من الملف. يرجى التحقق من صيغة الملف.")
                    
        except Exception as e:
            st.error(f"❌ حدث خطأ في معالجة الملف: {str(e)}")
            st.info("💡 تأكد من أن الملف يحتوي على البيانات المطلوبة وأن أعمدة الدرجات تحتوي على أرقام صحيحة.")
    
    else:
        # رسالة ترحيبية
        st.info("👋 مرحباً بك في منصة تحليل درجات الطلاب!")
        st.markdown("""
        ### 🎯 المزايا المتاحة:
        
        **📊 التحليل الإحصائي:**
        - حساب المتوسط والوسيط والانحراف المعياري
        - تحديد أعلى وأقل الدرجات
        - حساب نسب النجاح والرسوب
        
        **📈 المخططات التفاعلية:**
        - توزيع الدرجات (هستوجرام)
        - نسب النجاح والرسوب (مخطط دائري)
        - الدرجات حسب النطاقات (مخطط أعمدة)
        - تحليل البيانات (مخطط صندوقي)
        
        **📄 التقارير:**
        - تقرير شامل بصيغة Excel (يحتوي على ملخص، تفاصيل الطلاب، المتفوقين، المتعثرين، ونطاقات الدرجات)
        - تقرير شامل بصيغة PDF (للعرض والطباعة)
        - قوائم منفصلة للطلاب المتفوقين والمتعثرين
        - حساب النسب المئوية من الدرجة الكلية المحددة في العمود السادس
        
        **ابدأ برفع ملف Excel يحتوي على درجات الطلاب!**
        """)

if __name__ == "__main__":
    main()
