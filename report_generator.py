import json
from datetime import datetime
from typing import Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
    
    def generate_pdf(self, analysis: Dict, filename: str, output_path: str):
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        story.append(Paragraph("Resume Quality Analysis Report", self.title_style))
        story.append(Spacer(1, 0.2*inch))
        
        info_data = [
            ['Analysis Date:', datetime.now().strftime('%B %d, %Y')],
            ['Resume File:', filename],
            ['Target Role:', analysis.get('target_role', 'Not specified')],
            ['Career Stage:', analysis.get('career_stage', 'Unknown')]
        ]
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Overall Score", self.heading_style))
        overall_score = analysis.get('overall_score', 0)
        max_score = analysis.get('max_score', 120)
        verdict = analysis.get('verdict', 'Unknown')
        
        score_text = f"<b>{overall_score}/{max_score}</b> - {verdict}"
        story.append(Paragraph(score_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        categories = [
            ('Completeness', 'completeness'),
            ('Summary Quality', 'summary'),
            ('Education', 'education'),
            ('Employment', 'employment')
        ]
        
        for cat_name, cat_key in categories:
            story.append(Paragraph(cat_name, self.heading_style))
            cat_data = analysis.get(cat_key, {})
            score = cat_data.get('score', 0)
            max_score_cat = cat_data.get('max_score', 30)
            band = cat_data.get('band', 'Unknown')
            
            score_line = f"Score: <b>{score}/{max_score_cat}</b> ({band})"
            story.append(Paragraph(score_line, self.styles['Normal']))
            
            details = cat_data.get('details', [])
            if details:
                for detail in details[:5]:
                    story.append(Paragraph(f"• {detail}", self.styles['Normal']))
            
            story.append(Spacer(1, 0.15*inch))
        
        story.append(Paragraph("ATS Readiness", self.heading_style))
        ats = analysis.get('ats_readiness', {})
        verdict_ats = ats.get('verdict', 'Unknown')
        story.append(Paragraph(f"<b>Verdict: {verdict_ats}</b>", self.styles['Normal']))
        
        signals = ats.get('signals', [])
        if signals:
            story.append(Paragraph("Signals:", self.styles['Normal']))
            for signal in signals[:5]:
                story.append(Paragraph(f"• {signal}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.15*inch))
        
        recommendations = ats.get('recommendations', [])
        if recommendations:
            story.append(Paragraph("Recommendations:", self.styles['Normal']))
            for rec in recommendations[:5]:
                story.append(Paragraph(f"• {rec}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Role Alignment", self.heading_style))
        alignment = analysis.get('role_alignment', {})
        align_score = alignment.get('score', 0)
        story.append(Paragraph(f"Alignment Score: <b>{align_score}%</b>", self.styles['Normal']))
        story.append(Paragraph(alignment.get('alignment_details', ''), self.styles['Normal']))
        
        gaps = alignment.get('gaps', [])
        if gaps:
            story.append(Paragraph("Key Skills to Add:", self.styles['Normal']))
            for gap in gaps:
                story.append(Paragraph(f"• {gap}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        plan = analysis.get('improvement_plan', {})
        if plan:
            story.append(Paragraph("1-Year Improvement Plan", self.heading_style))
            
            if plan.get('skills_to_acquire'):
                story.append(Paragraph("<b>Skills to Acquire:</b>", self.styles['Normal']))
                for skill in plan['skills_to_acquire'][:5]:
                    story.append(Paragraph(f"• {skill}", self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            if plan.get('projects_to_build'):
                story.append(Paragraph("<b>Projects to Build:</b>", self.styles['Normal']))
                for project in plan['projects_to_build'][:5]:
                    story.append(Paragraph(f"• {project}", self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            if plan.get('quarterly_milestones'):
                story.append(Paragraph("<b>Quarterly Milestones:</b>", self.styles['Normal']))
                for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
                    milestones = plan['quarterly_milestones'].get(quarter, [])
                    if milestones:
                        story.append(Paragraph(f"<b>{quarter}:</b>", self.styles['Normal']))
                        for milestone in milestones[:3]:
                            story.append(Paragraph(f"  • {milestone}", self.styles['Normal']))
        
        doc.build(story)
    
    def generate_json(self, analysis: Dict, output_path: str):
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
