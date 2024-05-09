# import tempfile
# from weasyprint import HTML
# from fastapi import APIRouter

# down_pdf_router = APIRouter()

# @down_pdf_router.post("/generate-pdf")
# async def generate_pdf(review_content: str):
#     try:
#         html_content = f"<html><body>{review_content}</body></html>"
#         pdf_file = tempfile.NamedTemporaryFile(delete=False)
#         HTML(string=html_content).write_pdf(pdf_file.name)
#         return FileResponse(pdf_file.name, media_type='application/pdf')
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))