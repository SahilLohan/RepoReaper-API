## app/routers/generate_doc.py
from fastapi import APIRouter
from models.schemas import GenerateDocRequest, GenerateDocResponse
from services.generate_doc_service import ApiDocService
from fastapi.responses import JSONResponse
from fastapi import status
router = APIRouter()

@router.post("/generate-doc", response_model=GenerateDocResponse)
def generate_doc_router(request: GenerateDocRequest):
    try:
        markdownText = ApiDocService().generate_doc(language=request.language,repo_name=request.repo_name)

        if not markdownText:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "data": [],
                    "responseType": "error",
                    "status": "false",
                    "message": "Markdown not generated. Looks like the repo don't contains any api related code."
                }
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "data": markdownText,
                "responseType": "markdown",
                "status": "true",
                "message": "Markdown generated successfully"
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "data": [],
                "responseType": "error",
                "status": "false",
                "message": str(e)
            }
        )



