# from fastapi import APIRouter
# from fastapi import Response, Request
# from weasyprint import HTML
#
# down_pdf_router = APIRouter()
#
#
# @down_pdf_router.post('/generate-pdf')
# async def generate_pdf(request: Request, review_content: str):
#     print("Request Headers:", request.headers)
#     print("Request Body:", await request.body())
#
#     if not review_content:
#         return {"error": "review_content is required"}
#
#     try:
#         html_content = f"<html><body>{review_content}</body></html>"
#         pdf_file = HTML(string=html_content).write_pdf()
#         headers = {
#             'Content-Disposition': 'attachment; filename="review_content.pdf"'
#         }
#         return Response(pdf_file, headers=headers, media_type='application/pdf')
#     except Exception as e:
#         return {'error': str(e)}