from jinja2 import Template
import pdfkit
from Standardize import standardize_format

def generate_pdf(resume_data, output_pdf_path):
    # Define the HTML template for the resume
    resume_data = standardize_format(resume_data)
    resume_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ resume['name'] }} - Resume</title>
        <style>
            @page {
                size: A4;
                margin: 10mm;
            }
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-size: 10pt;
                color: #333;
            }
            .container {
                width: 100%;
                max-width: 100%;
                padding: 15px;
            }
            h1 {
                font-size: 24px;
                margin-bottom: 5px;
                color: #333;
            }
            p {
                margin: 2px 0;
                line-height: 1.4;
            }
            .header {
                text-align: center;
                margin-bottom: 15px;
            }
            .header p {
                margin: 0;
            }
            .section {
                margin-bottom: 15px;
                page-break-inside: avoid;
            }
            .section-header {
                font-size: 16px;
                font-weight: bold;
                border-bottom: 1px solid #ccc;
                margin-bottom: 10px;
                padding-bottom: 3px;
            }
            .section-content {
                margin-top: 5px;
            }
            .subsection {
                margin-bottom: 10px;
            }
            .subsection-header {
                font-size: 14px;
                font-weight: bold;
                color: #444;
            }
            .details {
                font-size: 10pt;
                color: #555;
            }
            .skills {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .skill {
                font-size: 9pt;
                background-color: #f0f0f0;
                padding: 3px 6px;
                border-radius: 3px;
            }
            ul {
                list-style-type: disc;
                margin-left: 20px;
                padding-left: 0;
                font-size: 9pt;
            }
            li {
                margin-bottom: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{{ resume['name'] }}</h1>
                <p>Email: {{ resume['email'] }} | Phone: {{ resume['phone'] }}</p>
                <p><a href="https://{{ resume['linkedin'] }}" target="_blank">LinkedIn</a> | <a href="https://{{ resume['github'] }}" target="_blank">GitHub</a></p>
            </div>

            {% if resume['summary'] %}
            <div class="section">
                <div class="section-header">Summary</div>
                <div class="section-content">
                    <p>{{ resume['summary'] }}</p>
                </div>
            </div>
            {% endif %}

            {% if resume['education'] %}
            <div class="section">
                <div class="section-header">Education</div>
                <div class="section-content">
                    {% for edu in resume['education'] %}
                    <div class="subsection">
                        <div class="subsection-header">{{ edu['institution'] }}</div>
                        <p class="details">{{ edu['degree'] }} | GPA: {{ edu['gpa'] }} | Graduation Date: {{ edu['graduationDate'] }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if resume['skills'] %}
            <div class="section">
                <div class="section-header">Skills</div>
                <div class="section-content">
                    <div class="skills">
                        {% for skill in resume['skills'] %}
                        <span class="skill">{{ skill }}</span>
                        {% endfor %}
                    </div>
                </div>
            </div>
            {% endif %}

            {% if resume['projects'] %}
            <div class="section">
                <div class="section-header">Projects</div>
                <div class="section-content">
                    {% for project in resume['projects'] %}
                    <div class="subsection">
                        <div class="subsection-header">{{ project['name'] }}</div>
                        <p>{{ project['description'] | join(', ') }}</p>
                        <p class="details"><strong>Technologies Used:</strong> {{ project['technologies'] | join(', ') }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if resume['experience'] %}
            <div class="section">
                <div class="section-header">Experience</div>
                <div class="section-content">
                    {% for exp in resume['experience'] %}
                    <div class="subsection">
                        <div class="subsection-header">{{ exp['title'] }} ({{ exp['startDate'] }} - {{ exp['endDate'] }})</div>
                        <p>{{ exp['company'] }}</p>
                        <ul>
                            {% for duty in exp['description'] %}
                            <li>{{ duty }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """

    # Render the template with the provided resume data
    template = Template(resume_template)
    # print(resume_data)
    # print(resume_data)
    rendered_html = template.render(resume=resume_data)

    # Convert the rendered HTML to a PDF
    pdfkit.from_string(rendered_html, output_pdf_path)

# Example usage
# resume_data = {...}  # Your resume data
# generate_pdf(resume_data, "processed_resume.pdf")
