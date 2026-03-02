import gradio as gr
from groq import Groq
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# -----------------------------
# GROQ CLIENT
# -----------------------------

API_KEY = os.getenv("GROQ_API_KEY") # Changed from hardcoded string to environment variable name

if not API_KEY:
    print("⚠️ GROQ_API_KEY not found in environment")

client = Groq(api_key=API_KEY)

# -----------------------------
# PDF GENERATOR
# -----------------------------

def create_pdf(text, filename="roadmap.pdf"):

    styles = getSampleStyleSheet()

    style_h = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"]
    )

    style_p = ParagraphStyle(
        "Body",
        parent=styles["BodyText"]
    )

    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []

    for line in text.split("\n"):
        if line.strip().startswith("##"):
            story.append(Paragraph(line.replace("##", ""), style_h))
        else:
            story.append(Paragraph(line, style_p))

        story.append(Spacer(1, 8))

    doc.build(story)

    return filename


# -----------------------------
# AI ROADMAP FUNCTION
# -----------------------------

def generate_ai_roadmap(domain, level, skills, duration):

    if not domain:
        return "Please enter a domain."

    prompt = f"""
You are an expert curriculum designer.
Create a FULL learning course roadmap in Markdown.
Structure:
## Course Overview
## Learning Objectives
## Complete Topic List (beginner → advanced)
## Phase-wise Breakdown
## Tools & Resources
## Practice Projects
## Final Capstone Project
Use emojis.
Make it stylish and clean.
Inputs:
Domain: {domain}
Level: {level}
Skills: {skills}
Time: {duration} weeks
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"Error generating roadmap:\n{str(e)}"


# -----------------------------
# GRADIO UI WITH PDF BUTTON
# -----------------------------

with gr.Blocks(theme=gr.themes.Soft()) as app:

    gr.Markdown("# Way To Learn")
    gr.Markdown("Generate a complete AI-powered learning course and download it as a PDF.")

    with gr.Row():
        domain = gr.Textbox(label="Domain / Field", placeholder="Machine Learning")
        level = gr.Dropdown(["Beginner", "Intermediate", "Advanced"], value="Beginner")
        skills = gr.Textbox(label="Current Skills")
        duration = gr.Slider(4, 32, step=1, label="Time to Learn (weeks)")

    generate_btn = gr.Button("Generate Roadmap")

    roadmap_output = gr.Markdown()

    pdf_btn = gr.Button("Download as PDF")
    pdf_file = gr.File()

    # Generate roadmap
    generate_btn.click(
        fn=generate_ai_roadmap,
        inputs=[domain, level, skills, duration],
        outputs=roadmap_output
    )

    # Convert to PDF
    def roadmap_to_pdf(text):
        path = create_pdf(text)
        return path

    pdf_btn.click(
        fn=roadmap_to_pdf,
        inputs=roadmap_output,
        outputs=pdf_file
    )

app.launch()
