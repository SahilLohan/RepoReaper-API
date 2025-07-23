import os
import json
import time
import re
from mistralai import Mistral
from services.repo_analysis_service import MultiLanguageApiAnalyzerService
from dotenv import load_dotenv
load_dotenv()

class ApiDocService:

    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY") # or hardcode your key here
        self.client = Mistral(api_key=api_key)

        env_model = os.getenv("MISTRAL_MODEL")
        self.model = env_model if env_model is not None else "mistral-small-latest"
        print("api key : ",api_key,"\nenv_model : ",env_model)

    def _summarize_files(self, file_paths: list[str], language: str ) -> list[dict]:
        aggregated = []
        PROMPT_TEMPLATE = """
You are an expert code analyst. Analyze the following code and extract all API-related components: endpoints, controllers, services, repositories, DTOs, models. Output must be a JSON array where each element includes:
- type (endpoint|service|repository|model)
- name
- signature
- description
- inputs: [{{name, type, description}}]
- outputs: [{{name, type, description}}]
- calls: [called components]

### Example 1: endpoint
[
  {{
    "type": "endpoint",
    "name": "getUser",
    "signature": "GET /api/user/{{id}}",
    "description": "Retrieve user by ID",
    "inputs": [{{"name": "id", "type": "int", "description": "User identifier"}}],
    "outputs": [{{"name": "200", "type": "UserDto", "description": "User details"}}],
    "calls": ["UserService.getById"]
  }}
]

### Example 2: service
[
  {{
    "type": "service",
    "name": "UserService.getById",
    "signature": "User getById(int id)",
    "description": "Fetches user entity from repository",
    "inputs": [{{"name": "id", "type": "int", "description": "User ID"}}],
    "outputs": [{{"name": "User", "type": "User", "description": "User entity"}}],
    "calls": ["UserRepository.find"]
  }}
]

### Example 3: repository
[
  {{
    "type": "repository",
    "name": "UserRepository.find",
    "signature": "Optional<User> find(int id)",
    "description": "Query the data store for a user by ID",
    "inputs": [{{"name": "id", "type": "int", "description": "User primary key"}}],
    "outputs": [{{"name": "User", "type": "User", "description": "Found user or null"}}],
    "calls": []
  }}
]

### Example 4: model
[
  {{
    "type": "model",
    "name": "LoginRequest",
    "signature": "class UserDto",
    "description": "Data transfer object for User",
    "inputs": [],
    "outputs": [],
    "fields": [
      {{"name": "id", "type": "int", "description": "Identifier"}},
      {{"name": "name", "type": "string", "description": "User full name"}}
    ],
    "calls": []
  }}
]

Generate the output descriptions in {language}.
Now analyze this code:
{code}
"""

        for path in file_paths:
            if not os.path.isfile(path):
                raise Exception(path+" : file not found")
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()

            print("Summarzing file : ",path)

            prompt = PROMPT_TEMPLATE.format(code=code, language=language)
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code analyst."},
                    {"role": "user", "content": prompt}
                ]
                # max_tokens=4096
            )
            raw_response = response.choices[0].message.content
            json_blocks = re.findall(r'```json\s*(.*?)\s*```', raw_response, re.DOTALL)
            
            elements = []
            for block in json_blocks:
                try:
                    data = json.loads(block)
                    for elem in data:
                        elem['file'] = os.path.basename(path)
                    elements.extend(data)
                except json.JSONDecodeError:
                    elements.append({
                        "type": "error",
                        "content": block.strip(),
                        "file": os.path.basename(path)
                    })

            # If nothing parsed, fallback to raw message
            if not elements:
                elements = [{
                    "type": "error",
                    "content": raw_response.strip(),
                    "file": os.path.basename(path)
                }]

            aggregated.extend(elements)
            time.sleep(1)

        return aggregated


    def _give_api_documentation_markdown(self,json_payload):

        MARKDOWN_EXAMPLE="""
# 🎬 Movie Review API Documentation

Welcome to the **Movie Review API**, where you can manage genres and user reviews.  
This doc covers endpoints, models, and example requests only.

---

## Endpoints

### 1. Create Genre  
**POST** `/Genres`  
**Description:** Create a new genre in the system.

**Request Body**  
```
{
"name": "Action"
}
```
text

**Example `curl`**  
```
curl -X POST "https://api.example.com/Genres"
-H "Content-Type: application/json"
-d '{"name":"Action"}'
```

---

### 2. Get All Genres  
**GET** `/Genres`  
**Description:** Retrieve a list of all genres.

**Example `curl`**  
```
curl -X GET "https://api.example.com/Genres"
-H "Accept: application/json"
```

---

### 3. Get Genre by ID  
**GET** `/Genres/{id}`  
**Description:** Retrieve a genre by its ID.

**Path Parameter**  
| Name | Type | Description |
|------|------|-------------|
| id   | int  | Genre ID    |

**Example `curl`**  
```
curl -X GET "https://api.example.com/Genres/1"
-H "Accept: application/json"
```

---

### 4. Update Genre  
**PUT** `/Genres/{id}`  
**Description:** Update an existing genre.

**Path Parameter**  
| Name | Type | Description |
|------|------|-------------|
| id   | int  | Genre ID    |

**Request Body**  
```
{
"name": "Adventure"
}
```
**Example `curl`**  
```
curl -X PUT "https://api.example.com/Genres/1"
-H "Content-Type: application/json"
-d '{"name":"Adventure"}'
```

---

### 5. Delete Genre  
**DELETE** `/Genres/{id}`  
**Description:** Delete a genre by its ID.

**Path Parameter**  
| Name | Type | Description |
|------|------|-------------|
| id   | int  | Genre ID    |

**Example `curl`**  
```
curl -X DELETE "https://api.example.com/Genres/1"
-H "Accept: application/json"
```

---

## Models

### LoginModel  
> Data transfer object for user login credentials  

| Field    | Type   | Description               |
|----------|--------|---------------------------|
| Username | string | User's login username     |
| Password | string | User's login password     |

---

### ReviewRequest  
> DTO for creating or updating a review  

| Field   | Type   | Description                  |
|---------|--------|------------------------------|
| MovieId | int    | Identifier of the movie      |
| UserId  | int    | Identifier of the user       |
| Rating  | int    | Rating value (1 to 5)        |
| Comment | string | User’s review comment        |

---
"""
        prompt=f"""
You are an expert technical writer specialized in API documentation.
Produce a comprehensive, elegant GitHub-flavored Markdown document
that fully describes every endpoint, model, and service in the JSON schema below.

=== EXAMPLE OUTPUT ===
{MARKDOWN_EXAMPLE}
=== END EXAMPLE ===

JSON schema:
{json_payload}
"""

        response = self.client.chat.complete(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert technical writer specialized in API documentation."},
                {"role": "user", "content": prompt}
            ]
        )
        raw_response = response.choices[0].message.content

        return raw_response


    def generate_doc(self, language:str,repo_name:str):
        try:
            language_files_paths=MultiLanguageApiAnalyzerService().get_files_by_language(repo_name=repo_name,target_language=language) # language files list[str]
            summaries_list=self._summarize_files(language_files_paths,language)
            markdown=self._give_api_documentation_markdown(summaries_list)
            return markdown
        except Exception as e:
            raise Exception(str(e))



def main():
    print(ApiDocService().generate_doc(language="JavaScript",repo_name="sample-node-api"))

if __name__ == "__main__":
    main()
