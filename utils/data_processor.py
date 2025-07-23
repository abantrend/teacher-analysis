import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Optional, Tuple
import io

class DataProcessor:
    """معالج البيانات لتحليل درجات الطلاب"""
    
    def __init__(self):
        self.passing_grade = 50  # درجة النجاح الافتراضية
    
    def load_excel_file(self, uploaded_file) -> Optional[pd.DataFrame]:
        """
        تحميل ملف Excel وتنظيف البيانات
        
        Args:
            uploaded_file: الملف المرفوع من Streamlit
            
        Returns:
            DataFrame محتوي على البيانات المنظفة أو None في حالة الخطأ
        """
        try:
            # التحقق من وجود الملف
            if uploaded_file is None:
                st.error("لم يتم رفع أي ملف")
                return None
                
            # قراءة الملف حسب الامتداد
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if file_extension == 'xlsx':
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            elif file_extension == 'xls':
                df = pd.read_excel(uploaded_file, engine='xlrd')
            else:
                st.error("نوع الملف غير مدعوم. يرجى استخدام ملفات .xlsx أو .xls")
                return None
            
            # التحقق من وجود البيانات
            if df is None or df.empty:
                st.error("الملف فارغ أو لا يحتوي على بيانات")
                return None
            
            # التحقق من وجود أعمدة كافية
            if len(df.columns) < 2:
                st.error("الملف يجب أن يحتوي على عمودين على الأقل (اسم الطالب والدرجة)")
                return None
            
            # تنظيف البيانات
            cleaned_df = self._clean_data(df)
            
            # التحقق من نجاح التنظيف
            if cleaned_df is None or cleaned_df.empty:
                st.error("لا توجد بيانات صالحة بعد التنظيف. تأكد من أن الملف يحتوي على أسماء طلاب ودرجات صحيحة")
                return None
            
            return cleaned_df
            
        except pd.errors.EmptyDataError:
            st.error("الملف فارغ أو تالف")
            return None
        except pd.errors.ParserError:
            st.error("خطأ في قراءة الملف. تأكد من أن الملف بصيغة Excel صحيحة")
            return None
        except UnicodeDecodeError:
            st.error("خطأ في ترميز الملف. تأكد من أن الملف محفوظ بترميز UTF-8")
            return None
        except Exception as e:
            st.error(f"خطأ غير متوقع في قراءة الملف: {str(e)}")
            st.info("نصائح لحل المشكلة:\n- تأكد من أن الملف بصيغة Excel (.xlsx أو .xls)\n- تأكد من أن الملف يحتوي على أسماء الطلاب في العمود الأول والدرجات في العمود الثاني\n- تأكد من أن الدرجات أرقام وليس نص")
            return None
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        تنظيف وتحضير البيانات حسب التصميم المحدد
        التصميم المطلوب:
        العمود 1: اسم الطالب
        العمود 2: الصف  
        العمود 3: الفصل
        العمود 4: درجة الطالب
        العمود 5: المادة
        العمود 6: درجة التصحيح من (الدرجة الكلية)
        العمود 7: اسم المعلم/المعلمة
        العمود 8: اسم المدير/المديرة
        
        Args:
            df: DataFrame الأصلي
            
        Returns:
            DataFrame منظف
        """
        # إنشاء DataFrame جديد مع الأعمدة المطلوبة
        cleaned_df = pd.DataFrame()
        
        # التحقق من وجود الأعمدة المطلوبة
        if len(df.columns) < 4:
            st.error("الملف يجب أن يحتوي على 4 أعمدة على الأقل (اسم الطالب، الصف، الفصل، درجة الطالب)")
            return pd.DataFrame()
        
        # الأعمدة الأساسية للعرض
        cleaned_df['اسم الطالب'] = df.iloc[:, 0].astype(str)  # العمود الأول
        cleaned_df['الصف'] = df.iloc[:, 1].astype(str)        # العمود الثاني
        cleaned_df['الفصل'] = df.iloc[:, 2].astype(str)       # العمود الثالث
        
        # تنظيف عمود الدرجات (العمود الرابع)
        grades = pd.to_numeric(df.iloc[:, 3], errors='coerce')
        cleaned_df['الدرجة'] = grades
        
        # الأعمدة الإضافية للتقارير والعمليات الحسابية
        if len(df.columns) >= 5:
            cleaned_df['المادة'] = df.iloc[:, 4].astype(str)
        
        if len(df.columns) >= 6:
            # درجة التصحيح من (الدرجة الكلية) - للنسبة المئوية
            total_grades = pd.to_numeric(df.iloc[:, 5], errors='coerce')
            cleaned_df['الدرجة الكلية'] = total_grades
            
            # حساب النسبة المئوية
            cleaned_df['النسبة المئوية'] = (cleaned_df['الدرجة'] / cleaned_df['الدرجة الكلية'] * 100).round(2)
        
        if len(df.columns) >= 7:
            cleaned_df['المعلم'] = df.iloc[:, 6].astype(str)
            
        if len(df.columns) >= 8:
            cleaned_df['المدير'] = df.iloc[:, 7].astype(str)
        
        # إزالة الصفوف التي تحتوي على قيم مفقودة في الأعمدة الأساسية
        cleaned_df = cleaned_df.dropna(subset=['اسم الطالب', 'الدرجة'])
        
        # إزالة الصفوف المكررة بناءً على اسم الطالب والصف والفصل
        cleaned_df = cleaned_df.drop_duplicates(subset=['اسم الطالب', 'الصف', 'الفصل'], keep='first')
        
        # فلترة الدرجات غير المنطقية (أقل من 0)
        cleaned_df = cleaned_df[cleaned_df['الدرجة'] >= 0]
        
        # إذا كان هناك درجة كلية، نتحقق من أن الدرجة لا تتجاوز الدرجة الكلية
        if 'الدرجة الكلية' in cleaned_df.columns:
            cleaned_df = cleaned_df[cleaned_df['الدرجة'] <= cleaned_df['الدرجة الكلية']]
        else:
            # إذا لم تكن هناك درجة كلية، نفترض أن الدرجة من 100
            cleaned_df = cleaned_df[cleaned_df['الدرجة'] <= 100]
        
        return cleaned_df.reset_index(drop=True)
    
    def calculate_basic_stats(self, df: pd.DataFrame) -> Dict:
        """
        حساب الإحصائيات الأساسية مع دعم الدرجة الكلية والنسبة المئوية
        
        Args:
            df: DataFrame يحتوي على البيانات
            
        Returns:
            قاموس يحتوي على الإحصائيات
        """
        grades = df['الدرجة']
        
        # الإحصائيات الأساسية للدرجات
        stats = {
            'count': len(grades),
            'mean': grades.mean(),
            'median': grades.median(),
            'std': grades.std(),
            'min': grades.min(),
            'max': grades.max(),
            'q1': grades.quantile(0.25),
            'q3': grades.quantile(0.75),
        }
        
        # إحصائيات الدرجة الكلية إن وجدت
        if 'الدرجة الكلية' in df.columns:
            total_grades = df['الدرجة الكلية']
            stats['total_mean'] = total_grades.mean()
            stats['total_max'] = total_grades.max()
            stats['total_min'] = total_grades.min()
        
        # إحصائيات النسبة المئوية إن وجدت
        if 'النسبة المئوية' in df.columns:
            percentages = df['النسبة المئوية']
            stats['percentage_mean'] = percentages.mean()
            stats['percentage_median'] = percentages.median()
            stats['percentage_std'] = percentages.std()
            
            # تحديد معيار النجاح بناءً على النسبة المئوية (50%)
            passing_percentage = 50
            passing_students = len(percentages[percentages >= passing_percentage])
            
            stats['pass_rate'] = (passing_students / len(percentages)) * 100
            stats['fail_rate'] = 100 - stats['pass_rate']
            stats['passing_count'] = passing_students
            stats['failing_count'] = len(percentages) - passing_students
        else:
            # استخدام معيار النجاح التقليدي (50 من 100)
            passing_students = len(grades[grades >= self.passing_grade])
            stats['pass_rate'] = (passing_students / len(grades)) * 100
            stats['fail_rate'] = 100 - stats['pass_rate']
            stats['passing_count'] = passing_students
            stats['failing_count'] = len(grades) - passing_students
        
        return stats
    
    def categorize_grades(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        تصنيف الدرجات حسب النطاقات بناءً على النسبة المئوية
        
        Args:
            df: DataFrame يحتوي على البيانات
            
        Returns:
            DataFrame يحتوي على التصنيفات
        """
        # استخدام النسبة المئوية إن وجدت، وإلا استخدام الدرجة مباشرة
        if 'النسبة المئوية' in df.columns:
            percentages = df['النسبة المئوية']
            total_students = len(percentages)
            
            # تعريف النطاقات بناءً على النسبة المئوية
            ranges = {
                'ممتاز (90-100%)': len(percentages[(percentages >= 90) & (percentages <= 100)]),
                'جيد جداً (80-89%)': len(percentages[(percentages >= 80) & (percentages < 90)]),
                'جيد (70-79%)': len(percentages[(percentages >= 70) & (percentages < 80)]),
                'مقبول (60-69%)': len(percentages[(percentages >= 60) & (percentages < 70)]),
                'ضعيف (50-59%)': len(percentages[(percentages >= 50) & (percentages < 60)]),
                'راسب (0-49%)': len(percentages[percentages < 50])
            }
        else:
            # استخدام الدرجة مباشرة (افتراض أنها من 100)
            grades = df['الدرجة']
            total_students = len(grades)
            
            ranges = {
                'ممتاز (90-100)': len(grades[(grades >= 90) & (grades <= 100)]),
                'جيد جداً (80-89)': len(grades[(grades >= 80) & (grades < 90)]),
                'جيد (70-79)': len(grades[(grades >= 70) & (grades < 80)]),
                'مقبول (60-69)': len(grades[(grades >= 60) & (grades < 70)]),
                'ضعيف (50-59)': len(grades[(grades >= 50) & (grades < 60)]),
                'راسب (0-49)': len(grades[grades < 50])
            }
        
        # إنشاء DataFrame للنتائج
        ranges_data = []
        for range_name, count in ranges.items():
            ranges_data.append([range_name, count])
        
        result_df = pd.DataFrame(ranges_data, columns=['النطاق', 'عدد الطلاب'])
        result_df['النسبة %'] = (result_df['عدد الطلاب'] / total_students * 100).round(1)
        
        return result_df
    
    def get_grade_details(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        الحصول على تفاصيل الدرجات مرتبة مع التصنيف الصحيح
        
        Args:
            df: DataFrame يحتوي على البيانات
            
        Returns:
            DataFrame مرتب حسب الدرجات
        """
        result_df = df.copy()
        
        # إضافة عمود التصنيف باستخدام النسبة المئوية إن وجدت
        def classify_grade(percentage):
            if percentage >= 90:
                return 'ممتاز'
            elif percentage >= 80:
                return 'جيد جداً'
            elif percentage >= 70:
                return 'جيد'
            elif percentage >= 60:
                return 'مقبول'
            elif percentage >= 50:
                return 'ضعيف'
            else:
                return 'راسب'
        
        # تحديد العمود المستخدم للتصنيف والحالة
        if 'النسبة المئوية' in result_df.columns:
            result_df['التصنيف'] = result_df['النسبة المئوية'].apply(classify_grade)
            result_df['الحالة'] = result_df['النسبة المئوية'].apply(lambda x: 'ناجح' if x >= 50 else 'راسب')
            # ترتيب حسب النسبة المئوية (تنازلي)
            result_df = result_df.sort_values('النسبة المئوية', ascending=False)
        else:
            result_df['التصنيف'] = result_df['الدرجة'].apply(classify_grade)
            result_df['الحالة'] = result_df['الدرجة'].apply(lambda x: 'ناجح' if x >= self.passing_grade else 'راسب')
            # ترتيب حسب الدرجة (تنازلي)
            result_df = result_df.sort_values('الدرجة', ascending=False)
        
        result_df = result_df.reset_index(drop=True)
        result_df.index = result_df.index + 1
        result_df = result_df.rename_axis('الترتيب')
        
        return result_df
    
    def get_top_students(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        الحصول على قائمة الطلاب المتفوقين
        
        Args:
            df: DataFrame يحتوي على البيانات
            top_n: عدد الطلاب المطلوب
            
        Returns:
            DataFrame يحتوي على الطلاب المتفوقين
        """
        # استخدام النسبة المئوية للترتيب إن وجدت
        if 'النسبة المئوية' in df.columns:
            top_students = df.nlargest(top_n, 'النسبة المئوية').copy()
        else:
            top_students = df.nlargest(top_n, 'الدرجة').copy()
            
        top_students = top_students.reset_index(drop=True)
        top_students.index = top_students.index + 1
        top_students = top_students.rename_axis('المرتبة')
        
        return top_students
    
    def get_failing_students(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        الحصول على قائمة الطلاب المتعثرين
        
        Args:
            df: DataFrame يحتوي على البيانات
            
        Returns:
            DataFrame يحتوي على الطلاب المتعثرين
        """
        # استخدام النسبة المئوية للتقييم إن وجدت
        if 'النسبة المئوية' in df.columns:
            failing_students = df[df['النسبة المئوية'] < 50].copy()
            failing_students = failing_students.sort_values('النسبة المئوية', ascending=True).reset_index(drop=True)
            failing_students['الفجوة'] = 50 - failing_students['النسبة المئوية']
        else:
            failing_students = df[df['الدرجة'] < self.passing_grade].copy()
            failing_students = failing_students.sort_values('الدرجة', ascending=True).reset_index(drop=True)
            failing_students['الفجوة'] = self.passing_grade - failing_students['الدرجة']
            
        failing_students.index = failing_students.index + 1
        
        return failing_students
    
    def get_statistical_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        ملخص إحصائي شامل
        
        Args:
            df: DataFrame يحتوي على البيانات
            
        Returns:
            DataFrame يحتوي على الملخص الإحصائي
        """
        grades = df['الدرجة']
        
        summary = pd.DataFrame({
            'الإحصائية': [
                'عدد الطلاب',
                'المتوسط الحسابي',
                'الوسيط',
                'المنوال',
                'الانحراف المعياري',
                'أقل درجة',
                'أعلى درجة',
                'المدى',
                'الربع الأول (Q1)',
                'الربع الثالث (Q3)',
                'المدى الربعي (IQR)',
                'نسبة النجاح',
                'نسبة الرسوب'
            ],
            'القيمة': [
                len(grades),
                f"{grades.mean():.2f}",
                f"{grades.median():.2f}",
                f"{grades.mode().iloc[0]:.2f}" if not grades.mode().empty else "N/A",
                f"{grades.std():.2f}",
                f"{grades.min():.2f}",
                f"{grades.max():.2f}",
                f"{grades.max() - grades.min():.2f}",
                f"{grades.quantile(0.25):.2f}",
                f"{grades.quantile(0.75):.2f}",
                f"{grades.quantile(0.75) - grades.quantile(0.25):.2f}",
                f"{len(grades[grades >= self.passing_grade]) / len(grades) * 100:.1f}%",
                f"{len(grades[grades < self.passing_grade]) / len(grades) * 100:.1f}%"
            ]
        })
        
        return summary
