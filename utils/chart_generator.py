import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict

class ChartGenerator:
    """مولد المخططات البيانية التفاعلية"""
    
    def __init__(self):
        # الألوان المستخدمة في المخططات
        self.colors = {
            'primary': '#1f77b4',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17becf',
            'purple': '#9467bd'
        }
    
    def create_histogram(self, df: pd.DataFrame) -> go.Figure:
        """
        إنشاء مخطط هستوجرام لتوزيع الدرجات أو النسب المئوية
        
        Args:
            df: DataFrame يحتوي على البيانات
            
        Returns:
            Plotly Figure
        """
        fig = go.Figure()
        
        # استخدام النسبة المئوية إن وجدت، وإلا استخدام الدرجة
        if 'النسبة المئوية' in df.columns:
            data_column = df['النسبة المئوية']
            mean_value = data_column.mean()
            title = "📊 توزيع النسب المئوية للطلاب"
            x_title = "النسبة المئوية (%)"
            success_line = 50
            success_text = "نسبة النجاح: 50%"
            mean_text = f"المتوسط: {mean_value:.1f}%"
        else:
            data_column = df['الدرجة']
            mean_value = data_column.mean()
            title = "📊 توزيع درجات الطلاب"
            x_title = "الدرجة"
            success_line = 50
            success_text = "درجة النجاح: 50"
            mean_text = f"المتوسط: {mean_value:.1f}"
        
        fig.add_trace(go.Histogram(
            x=data_column,
            nbinsx=20,
            name='توزيع الدرجات',
            marker_color=self.colors['primary'],
            opacity=0.7,
            text=[],
            texttemplate='%{y}',
            textposition='outside'
        ))
        
        # إضافة خط المتوسط
        fig.add_vline(
            x=mean_value,
            line_dash="dash",
            line_color=self.colors['danger'],
            annotation_text=mean_text,
            annotation_position="top"
        )
        
        # إضافة خط معيار النجاح
        fig.add_vline(
            x=success_line,
            line_dash="dot",
            line_color=self.colors['warning'],
            annotation_text=success_text,
            annotation_position="bottom"
        )
        
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title="عدد الطلاب",
            showlegend=False,
            template="plotly_white",
            font=dict(family="Arial", size=12),
            title_x=0.5
        )
        
        return fig
    
    def create_pie_chart(self, stats: Dict) -> go.Figure:
        """
        إنشاء مخطط دائري لنسب النجاح والرسوب
        
        Args:
            stats: قاموس الإحصائيات
            
        Returns:
            Plotly Figure
        """
        labels = ['ناجح', 'راسب']
        values = [stats['passing_count'], stats['failing_count']]
        colors = [self.colors['success'], self.colors['danger']]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent+value',
            textfont=dict(size=14),
            hovertemplate='<b>%{label}</b><br>' +
                         'العدد: %{value}<br>' +
                         'النسبة: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title="🥧 نسبة النجاح والرسوب",
            template="plotly_white",
            font=dict(family="Arial", size=12),
            title_x=0.5,
            annotations=[dict(text=f'{len(values)} طالب', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        return fig
    
    def create_bar_chart(self, grade_ranges: pd.DataFrame) -> go.Figure:
        """
        إنشاء مخطط أعمدة للدرجات حسب النطاق
        
        Args:
            grade_ranges: DataFrame يحتوي على نطاقات الدرجات
            
        Returns:
            Plotly Figure
        """
        colors_list = [
            self.colors['success'],   # ممتاز
            self.colors['info'],      # جيد جداً  
            self.colors['primary'],   # جيد
            self.colors['warning'],   # مقبول
            self.colors['purple'],    # ضعيف
            self.colors['danger']     # راسب
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=grade_ranges['النطاق'],
            y=grade_ranges['عدد الطلاب'],
            marker_color=colors_list[:len(grade_ranges)],
            text=grade_ranges['عدد الطلاب'],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                         'عدد الطلاب: %{y}<br>' +
                         'النسبة: %{customdata}%<br>' +
                         '<extra></extra>',
            customdata=grade_ranges['النسبة %']
        ))
        
        fig.update_layout(
            title="📊 توزيع الطلاب حسب النطاقات",
            xaxis_title="النطاق",
            yaxis_title="عدد الطلاب",
            template="plotly_white",
            font=dict(family="Arial", size=12),
            title_x=0.5,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_box_plot(self, df: pd.DataFrame) -> go.Figure:
        """
        إنشاء مخطط صندوقي لتحليل البيانات
        
        Args:
            df: DataFrame يحتوي على البيانات
            
        Returns:
            Plotly Figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=df['الدرجة'],
            name="درجات الطلاب",
            marker_color=self.colors['primary'],
            boxpoints='outliers',
            jitter=0.3,
            pointpos=-1.8,
            hoveron='points',
            hovertemplate='الدرجة: %{y}<br><extra></extra>'
        ))
        
        # إضافة خطوط مرجعية
        mean_grade = df['الدرجة'].mean()
        fig.add_hline(
            y=mean_grade,
            line_dash="dash",
            line_color=self.colors['danger'],
            annotation_text=f"المتوسط: {mean_grade:.1f}",
            annotation_position="right"
        )
        
        fig.add_hline(
            y=50,
            line_dash="dot",
            line_color=self.colors['warning'],
            annotation_text="درجة النجاح: 50",
            annotation_position="left"
        )
        
        fig.update_layout(
            title="📦 المخطط الصندوقي للدرجات",
            yaxis_title="الدرجة",
            template="plotly_white",
            font=dict(family="Arial", size=12),
            title_x=0.5,
            showlegend=False
        )
        
        return fig
    
    def create_grade_distribution_line(self, df: pd.DataFrame) -> go.Figure:
        """
        إنشاء مخطط خطي لتوزيع الدرجات
        
        Args:
            df: DataFrame يحتوي على البيانات
            
        Returns:
            Plotly Figure
        """
        # ترتيب البيانات حسب الدرجة
        sorted_df = df.sort_values('الدرجة').reset_index(drop=True)
        sorted_df['الترتيب'] = range(1, len(sorted_df) + 1)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sorted_df['الترتيب'],
            y=sorted_df['الدرجة'],
            mode='lines+markers',
            name='توزيع الدرجات',
            line=dict(color=self.colors['primary'], width=2),
            marker=dict(size=4),
            hovertemplate='الترتيب: %{x}<br>' +
                         'الدرجة: %{y}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title="📈 منحنى توزيع الدرجات",
            xaxis_title="ترتيب الطالب",
            yaxis_title="الدرجة",
            template="plotly_white",
            font=dict(family="Arial", size=12),
            title_x=0.5,
            showlegend=False
        )
        
        return fig
    
    def create_comparative_chart(self, stats: Dict) -> go.Figure:
        """
        إنشاء مخطط مقارن للإحصائيات
        
        Args:
            stats: قاموس الإحصائيات
            
        Returns:
            Plotly Figure
        """
        metrics = ['المتوسط', 'الوسيط', 'أعلى درجة', 'أقل درجة']
        values = [stats['mean'], stats['median'], stats['max'], stats['min']]
        colors_list = [self.colors['primary'], self.colors['info'], 
                      self.colors['success'], self.colors['danger']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=metrics,
            y=values,
            marker_color=colors_list,
            text=[f"{v:.1f}" for v in values],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                         'القيمة: %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title="📊 مقارنة الإحصائيات الأساسية",
            xaxis_title="الإحصائية",
            yaxis_title="القيمة",
            template="plotly_white",
            font=dict(family="Arial", size=12),
            title_x=0.5,
            showlegend=False
        )
        
        return fig
