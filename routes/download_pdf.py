import pdfkit
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from pathlib import Path

down_pdf_router = APIRouter()

# Configure the upload directory path
UPLOAD_DIR = Path("../Download-Files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

# Path to wkhtmltopdf executable
wkhtmltopdf_path = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
# Configure pdfkit with the path to wkhtmltopdf
pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)


@down_pdf_router.post('/generate-pdf')
async def generate_pdf(request: Request):
    data = await request.json()
    review_content = data.get("reviewContent", "")
    suggestion_content = data.get("suggestionContent", "")
    refer_links_content = data.get("referLinksContent", "")
    file_name = "This Is Paste Code Option Submission" if data.get("selectedFileName", "") == "" else data.get("selectedFileName", "")
    project_name = data.get("projectName", "")
    language = data.get("language", "")
    description = data.get("description", "")
    code = data.get("selectedFileContent", "")

    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{project_name}-Code Review</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    border: 3px solid #ddd; 
                    padding: 20px; 
                }}
                h1, h2 {{
                    color: #333;
                }}
                pre {{
                    background: #f4f4f4;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    font-size: 16px; /* Increase font size to 16px */
                }}
            </style>
        </head>
        <body>
            <p>
                <h2>Project Name - </h2>
                <pre>{project_name}</pre>
            </p>
            
            <p>
                <h2>File Name - </h2>
                <pre>{file_name}</pre>
            </p>
            
            <p>
                <h2>Language - </h2>
                <pre>{language}</pre>
            </p>
            
            <p>
                <h2>Description - </h2>
                <pre>{description}</pre>
            </p>
            
            <p>
                <h1>Review</h1>
                <pre>{review_content}</pre>
            </p>
            
            <p>
                <h1>Suggestions</h1>
                <pre>{suggestion_content}</pre>
            </p>
            
            <p>
                <h1>Refer Links</h1>
                <pre>{refer_links_content}</pre>
            </p>
            
            <p>
                <h1>Code</h1>
                <pre>{code}</pre>
            </p>
        </body>
    </html>
    """

    # Generate PDF file
    pdf_file_name = f'{project_name} Review.pdf'
    pdf_file_path = UPLOAD_DIR / pdf_file_name
    pdfkit.from_string(html_content, pdf_file_path, configuration=pdfkit_config)

    # Return the generated PDF file as a response
    return FileResponse(pdf_file_path, media_type='application/pdf', filename=f'{file_name}.pdf')
