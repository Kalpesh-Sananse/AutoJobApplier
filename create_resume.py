"""
Generate a professional-looking PDF resume for testing.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_dummy_resume():
    """Create a professional PDF resume."""
    
    # Create PDF
    doc = SimpleDocTemplate("dummy_resume.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#0073b1',
        spaceAfter=6,
        spaceBefore=12
    )
    
    # Header
    story.append(Paragraph("Alex Danny", title_style))
    story.append(Paragraph("Software Engineer", styles['Normal']))
    story.append(Paragraph("alex.danny@email.com | (555) 123-4567 | New York, NY 10001", styles['Normal']))
    story.append(Paragraph("linkedin.com/in/alexdanny | github.com/alexdanny", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    story.append(Paragraph(
        "Experienced Software Engineer with 5+ years of expertise in full-stack development, "
        "cloud architecture, and agile methodologies. Proven track record of delivering scalable "
        "solutions and leading cross-functional teams. "
        "Proficient in Python, JavaScript, React, Node.js, and AWS.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Skills
    story.append(Paragraph("TECHNICAL SKILLS", heading_style))
    story.append(Paragraph(
        "<b>Languages:</b> Python, JavaScript, TypeScript, Java, SQL<br/>"
        "<b>Frameworks:</b> React, Node.js, Django, Flask, Express.js<br/>"
        "<b>Cloud & Tools:</b> AWS, Docker, Kubernetes, Git, CI/CD<br/>"
        "<b>Databases:</b> PostgreSQL, MongoDB, Redis, DynamoDB",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Experience
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))
    
    story.append(Paragraph("<b>Senior Software Engineer</b> | TechCorp Inc. | New York, NY", styles['Normal']))
    story.append(Paragraph("<i>January 2021 - Present</i>", styles['Normal']))
    story.append(Paragraph(
        "• Led development of microservices architecture serving 1M+ daily users<br/>"
        "• Improved system performance by 40% through database optimization<br/>"
        "• Mentored team of 5 junior developers in best practices<br/>"
        "• Implemented CI/CD pipeline reducing deployment time by 60%",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("<b>Software Engineer</b> | StartupXYZ | Brooklyn, NY", styles['Normal']))
    story.append(Paragraph("<i>June 2019 - December 2020</i>", styles['Normal']))
    story.append(Paragraph(
        "• Built RESTful APIs using Node.js and Express.js<br/>"
        "• Developed React-based admin dashboard with 50+ features<br/>"
        "• Collaborated with product team to define technical requirements<br/>"
        "• Reduced API response time by 35% through caching strategies",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Education
    story.append(Paragraph("EDUCATION", heading_style))
    story.append(Paragraph(
        "<b>Bachelor of Science in Computer Science</b><br/>"
        "New York University | Graduated May 2019 | GPA: 3.8/4.0",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Certifications
    story.append(Paragraph("CERTIFICATIONS", heading_style))
    story.append(Paragraph(
        "• AWS Certified Solutions Architect - Associate<br/>"
        "• Google Cloud Professional Developer<br/>"
        "• Certified Scrum Master (CSM)",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(story)
    print("✅ Created dummy_resume.pdf")

if __name__ == "__main__":
    create_dummy_resume()
