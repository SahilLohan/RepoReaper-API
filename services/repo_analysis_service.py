# git_clone_service.py
from git import Repo, GitCommandError
from pathlib import Path

import os
import re
from typing import List, Dict, Optional, Set, Tuple

class GitCloneService:
    def __init__(self, base_folder: str = "data"):
        self.base_folder = Path(__file__).parent / base_folder
        self.base_folder.mkdir(exist_ok=True)

    def clone_repo(self, repo_url: str) -> dict:
        """
        Clone a GitHub repo into 'data/<repo_name>' or return existing clone.
        Returns:
          - repo_path: str
          - commit_sha: str
        Raises RuntimeError on failure.
        """
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        dest = self.base_folder / repo_name

        try:
            if dest.exists():
                repo = Repo(str(dest))
                sha = repo.head.commit.hexsha
                return {"repo_path": str(dest), "commit_sha": sha}

            repo = Repo.clone_from(repo_url, str(dest))
            sha = repo.head.commit.hexsha
            return {"repo_path": str(dest), "commit_sha": sha}

        except GitCommandError as e:
            raise RuntimeError(f"Clone failed: {e}")

class MultiLanguageApiAnalyzerService:
    """
    Enhanced service class for detecting programming languages and analyzing API-related files
    across C#, Java, Node.js, and Python ecosystems.
    """
    
    def __init__(self):
        # Programming language file extension mappings
        self.language_extensions = {
            'C#': ['.cs', '.csx'],
            'Python': ['.py', '.pyw', '.pyi'],
            'JavaScript': ['.js', '.jsx', '.mjs', '.cjs'],
            'TypeScript': ['.ts', '.tsx'],
            'Java': ['.java'],
            'JSON': ['.json'],
            'XML': ['.xml', '.xaml', '.xsd'],
            'YAML': ['.yaml', '.yml'],
            'HTML': ['.html', '.htm'],
            'CSS': ['.css', '.scss', '.sass', '.less'],
        }
        
        # Reverse mapping for quick lookup
        self.extension_to_language = {}

        for language, extensions in self.language_extensions.items():
            for ext in extensions:
                if ext not in self.extension_to_language:
                    self.extension_to_language[ext] = []
                self.extension_to_language[ext].append(language)
        
    def detect_language_from_extensions(self, directory_path: str) -> Dict[str, List[str]]:
        """
        Function 1: Detect programming languages used in a directory based on file extensions.
        """
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory path does not exist: {directory_path}")
        
        detected_languages = {}
        found_extensions = set()
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = Path(file)
                extension = file_path.suffix.lower()
                
                if extension:
                    found_extensions.add(extension)
        
        # Map extensions to languages
        for ext in found_extensions:
            if ext in self.extension_to_language:
                for language in self.extension_to_language[ext]:
                    if language not in detected_languages:
                        detected_languages[language] = []
                    if ext not in detected_languages[language]:
                        detected_languages[language].append(ext)
        
        return detected_languages

    def get_files_by_language(self, repo_name: str, target_language: str) -> List[str]:
        """
        Function 2: Get a list of all files (with relative paths) for a specific programming language.
        """
        if not os.path.isabs(repo_name):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            repo_name = os.path.join(current_dir,"data\\", repo_name)

        if not os.path.exists(repo_name):
            raise ValueError(f"Directory path does not exist: {repo_name}")
        
        if target_language not in self.language_extensions:
            available_languages = list(self.language_extensions.keys())
            raise ValueError(f"Language '{target_language}' not supported. Available languages: {available_languages}")
        
        target_extensions = self.language_extensions[target_language]
        matching_files = []
        
        for root, dirs, files in os.walk(repo_name):
            for file in files:
                file_path = Path(file)
                extension = file_path.suffix.lower()
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, "./")
                
                if extension in [ext.lower() for ext in target_extensions]:
                    matching_files.append(relative_path)
        return matching_files
        
    def detect_supported_languages(self,directory_path:str) -> List[str]:
        # Step 1: Detect all languages in the directory
        detected_languages = self.detect_language_from_extensions(directory_path)
        print(f"Detected languages: {list(detected_languages.keys())}")
        
        # Step 2: Filter to only supported API languages (C#, Java, Python, JavaScript, TypeScript)
        supported_api_languages = ['C#', 'Java', 'Python', 'JavaScript', 'TypeScript']
        api_languages = [lang for lang, exts in detected_languages.items() 
                        if lang in supported_api_languages]
        
        if not api_languages:
            print("No supported API languages found (C#, Java, Python, JavaScript, TypeScript)")
            return []
        
        return api_languages
    
    def get_repo_path(self, repo_url:str)->str:
        return repo_url.rstrip("/").split("/")[-1].replace(".git", "")

    def clone_repo_and_give_language_choices(self, repo_url: str):
        """
        Clones the repository and returns a list of supported programming languages found in it.
        """
        try:
            result={}
            git_clone_service = GitCloneService("data")
            result = git_clone_service.clone_repo(repo_url)

            repo_path = result.get("repo_path")
            
            if not repo_path or not os.path.exists(repo_path):
                raise FileNotFoundError(f"Repository path '{repo_path}' does not exist on the server.")

            # repo_path=""
            languages=self.detect_supported_languages(repo_path)

            lang_count={}
            print("languages : ",languages)
            for lang in languages:
                file_count=len(self.get_files_by_language(repo_name=repo_path,target_language=lang))
                lang_count[lang]=file_count
            
            return lang_count


        except Exception as e:
            print(f"Error in cloning or analyzing repo: {str(e)}")
            raise Exception(f"Failed to clone or analyze repository: {str(e)}")
        


if __name__ == '__main__':
    print(MultiLanguageApiAnalyzerService().clone_repo_and_give_language_choices("https://github.com/zowe/sample-node-api"))
    # print(MultiLanguageApiAnalyzerService().clone_repo_and_give_language_choices("https://github.com/SahilLohan/MovieMania-API"))

    # print(MultiLanguageApiAnalyzerService().get_repo_path("https://github.com/SahilLohan/MovieMania-API"))
    # print(MultiLanguageApiAnalyzerService().get_repo_path("https://github.com/zowe/sample-node-api"))

    # print(MultiLanguageApiAnalyzerService().get_files_by_language("MovieMania-API","Python"))
    print(MultiLanguageApiAnalyzerService().get_files_by_language("sample-node-api","JavaScript"))