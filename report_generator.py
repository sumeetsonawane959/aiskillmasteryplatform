"""
PDF report generator with graphs using matplotlib and reportlab.
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt


class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12
        )
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=12
        )

    def generate_score_progression_graph(self, sessions: List[Dict], output_path: str):
        """Generate score progression graph over time."""
        if not sessions:
            return None
        
        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda x: x['created_at'])
        
        dates = [datetime.fromisoformat(s['created_at']).strftime('%Y-%m-%d') for s in sorted_sessions]
        scores = [s['score'] for s in sorted_sessions]
        
        plt.figure(figsize=(10, 6))
        plt.plot(dates, scores, marker='o', linewidth=2, markersize=8, color='#1f77b4')
        plt.fill_between(range(len(dates)), scores, alpha=0.3, color='#1f77b4')
        plt.title('Score Progression Over Time', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Score', fontsize=12)
        plt.ylim(0, 100)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path

    def generate_question_wise_graph(self, evaluation: Dict, output_path: str):
        """Generate question-wise performance graph."""
        breakdown = evaluation.get('question_wise_breakdown', [])
        if not breakdown:
            return None
        
        indices = [item['question_index'] + 1 for item in breakdown]
        scores = [item['score'] for item in breakdown]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(indices, scores, color='#2ecc71', alpha=0.7, edgecolor='#27ae60', linewidth=1.5)
        plt.title('Question-wise Performance', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Question Number', fontsize=12)
        plt.ylabel('Score', fontsize=12)
        plt.ylim(0, 100)
        plt.xticks(indices)
        plt.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{score:.1f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path

    def generate_pdf_report(self, user_email: str, skill_name: str, 
                           evaluation: Dict, sessions: List[Dict], 
                           output_path: str):
        """Generate a comprehensive PDF report."""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("AI Learning & Skill Mastery Report", self.title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # User info
        story.append(Paragraph(f"<b>User:</b> {user_email}", self.body_style))
        story.append(Paragraph(f"<b>Skill:</b> {skill_name}", self.body_style))
        story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.body_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Overall Score
        overall_score = evaluation.get('overall_score', 0)
        score_color_hex = '#27ae60' if overall_score >= 70 else '#e74c3c'
        story.append(Paragraph(f"<b>Overall Score: <font color='{score_color_hex}'> {overall_score:.1f}%</font></b>", 
                              self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Score Progression Graph
        if len(sessions) > 1:
            graph_path = "temp_score_progression.png"
            self.generate_score_progression_graph(sessions, graph_path)
            if os.path.exists(graph_path):
                img = Image(graph_path, width=6*inch, height=3.6*inch)
                story.append(Paragraph("Score Progression Over Time", self.heading_style))
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
        
        # Question-wise Performance Graph
        graph_path2 = "temp_question_wise.png"
        self.generate_question_wise_graph(evaluation, graph_path2)
        if os.path.exists(graph_path2):
            img = Image(graph_path2, width=6*inch, height=3.6*inch)
            story.append(Paragraph("Question-wise Performance", self.heading_style))
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        
        # Question-wise Breakdown
        story.append(Paragraph("Detailed Question-wise Breakdown", self.heading_style))
        breakdown = evaluation.get('question_wise_breakdown', [])
        if breakdown:
            table_data = [['Question', 'Score', 'Feedback']]
            for item in breakdown:
                q_num = item.get('question_index', 0) + 1
                score = item.get('score', 0)
                feedback = item.get('feedback', '')[:100] + '...' if len(item.get('feedback', '')) > 100 else item.get('feedback', '')
                table_data.append([f"Q{q_num}", f"{score:.1f}%", feedback])
            
            table = Table(table_data, colWidths=[1*inch, 1.5*inch, 4.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
        
        # Strengths
        strengths = evaluation.get('strengths', [])
        if strengths:
            story.append(Paragraph("Strengths", self.heading_style))
            for strength in strengths:
                story.append(Paragraph(f"• {strength}", self.body_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Weaknesses
        weaknesses = evaluation.get('weaknesses', [])
        if weaknesses:
            story.append(Paragraph("Areas for Improvement", self.heading_style))
            for weakness in weaknesses:
                story.append(Paragraph(f"• {weakness}", self.body_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Study Recommendations
        recommendations = evaluation.get('study_recommendations', [])
        if recommendations:
            story.append(Paragraph("Study Recommendations", self.heading_style))
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", self.body_style))
        
        # Build PDF
        doc.build(story)
        
        # Cleanup temp files
        for temp_file in ["temp_score_progression.png", "temp_question_wise.png"]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

