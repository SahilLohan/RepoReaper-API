
## app/routers/analyze_repo.py
from fastapi import APIRouter
from models.schemas import AnalyzeRepoRequest, AnalyzeRepoResponse
from services.repo_analysis_service import MultiLanguageApiAnalyzerService
from fastapi.responses import JSONResponse
from fastapi import status
router = APIRouter()

# supported_api_languages = ['C#', 'Java', 'Python', 'JavaScript', 'TypeScript']

@router.post("/analyze-repo", response_model=AnalyzeRepoResponse)
def analyze_repo_router(request: AnalyzeRepoRequest):
    print("analyze repo request recieved")
    try:
        lang_list = MultiLanguageApiAnalyzerService().clone_repo_and_give_language_choices(request.repo_url)
        repo_name = MultiLanguageApiAnalyzerService().get_repo_path(request.repo_url)

        if not lang_list:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "data": [],
                    "responseType": "error",
                    "status": "false",
                    "message": "No supported language found.",

                }
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "data": lang_list,
                "responseType": "language_choice",
                "status": "true",
                "message": "This repository contains these programming languages. Please select a language to proceed.",
                "repo_name":repo_name
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



