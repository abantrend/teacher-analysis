import streamlit as st
import os
from typing import Dict, Optional

class AuthHandler:
    """معالج المصادقة باستخدام Replit Auth"""
    
    def __init__(self):
        self.replit_user_id = os.getenv('REPL_OWNER', None)
        self.replit_slug = os.getenv('REPL_SLUG', None)
        
    def is_authenticated(self) -> bool:
        """
        التحقق من حالة المصادقة
        
        Returns:
            True إذا كان المستخدم مصادق عليه
        """
        # التحقق من معلومات Replit
        if self.replit_user_id:
            return True
            
        # التحقق من session state
        return st.session_state.get('authenticated', False)
    
    def login(self) -> bool:
        """
        عملية تسجيل الدخول
        
        Returns:
            True في حالة نجاح تسجيل الدخول
        """
        try:
            # في بيئة Replit، المستخدم مصادق عليه تلقائياً
            if self.replit_user_id:
                st.session_state['authenticated'] = True
                st.session_state['user_info'] = {
                    'name': self.replit_user_id,
                    'id': self.replit_user_id,
                    'repl': self.replit_slug or 'منصة تحليل الدرجات'
                }
                return True
            
            # للبيئات الأخرى، استخدام مصادقة أساسية
            st.session_state['authenticated'] = True
            st.session_state['user_info'] = {
                'name': 'مستخدم النظام',
                'id': 'system_user',
                'repl': 'منصة تحليل الدرجات'
            }
            return True
            
        except Exception as e:
            st.error(f"خطأ في تسجيل الدخول: {str(e)}")
            return False
    
    def logout(self):
        """تسجيل الخروج"""
        st.session_state['authenticated'] = False
        if 'user_info' in st.session_state:
            del st.session_state['user_info']
        
        # مسح أي بيانات أخرى في الجلسة
        for key in list(st.session_state.keys()):
            if str(key).startswith('data_'):
                del st.session_state[key]
    
    def get_user_info(self) -> Dict:
        """
        الحصول على معلومات المستخدم
        
        Returns:
            قاموس يحتوي على معلومات المستخدم
        """
        if self.is_authenticated():
            return st.session_state.get('user_info', {
                'name': self.replit_user_id or 'مستخدم غير معروف',
                'id': self.replit_user_id or 'unknown',
                'repl': self.replit_slug or 'منصة تحليل الدرجات'
            })
        
        return {}
    
    def get_user_permissions(self) -> Dict:
        """
        الحصول على صلاحيات المستخدم
        
        Returns:
            قاموس يحتوي على الصلاحيات
        """
        if not self.is_authenticated():
            return {}
        
        # صلاحيات افتراضية لجميع المستخدمين المصادق عليهم
        permissions = {
            'can_upload_files': True,
            'can_view_reports': True,
            'can_download_reports': True,
            'can_view_statistics': True,
            'max_file_size_mb': 10,  # حد أقصى لحجم الملف
            'max_students': 1000     # حد أقصى لعدد الطلاب
        }
        
        # صلاحيات إضافية لمالك المشروع
        if self.replit_user_id:
            permissions.update({
                'is_admin': True,
                'can_modify_settings': True,
                'max_file_size_mb': 50,
                'max_students': 5000
            })
        
        return permissions
    
    def check_file_permission(self, file_size_bytes: int) -> bool:
        """
        التحقق من صلاحية رفع الملف
        
        Args:
            file_size_bytes: حجم الملف بالبايت
            
        Returns:
            True إذا كان مسموح برفع الملف
        """
        permissions = self.get_user_permissions()
        max_size_bytes = permissions.get('max_file_size_mb', 10) * 1024 * 1024
        
        return file_size_bytes <= max_size_bytes
    
    def check_student_count_permission(self, student_count: int) -> bool:
        """
        التحقق من صلاحية عدد الطلاب
        
        Args:
            student_count: عدد الطلاب
            
        Returns:
            True إذا كان العدد مسموح
        """
        permissions = self.get_user_permissions()
        max_students = permissions.get('max_students', 1000)
        
        return student_count <= max_students
    
    def log_activity(self, activity: str, details: Optional[str] = None):
        """
        تسجيل نشاط المستخدم
        
        Args:
            activity: نوع النشاط
            details: تفاصيل إضافية
        """
        if not self.is_authenticated():
            return
        
        user_info = self.get_user_info()
        
        # في هذا التطبيق، نحفظ النشاط في session state فقط
        if 'user_activities' not in st.session_state:
            st.session_state['user_activities'] = []
        
        activity_log = {
            'user': user_info.get('name', 'unknown'),
            'activity': activity,
            'details': details,
            'timestamp': st.session_state.get('current_time', 'unknown')
        }
        
        st.session_state['user_activities'].append(activity_log)
        
        # الاحتفاظ بآخر 50 نشاط فقط
        if len(st.session_state['user_activities']) > 50:
            st.session_state['user_activities'] = st.session_state['user_activities'][-50:]
