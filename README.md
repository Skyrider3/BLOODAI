# BLOOD AI

## Installation

```bash
python3 -m pip install uvicorn[standard]
pip3 install python-multipart
pip3 install --upgrade openai
pip3 install -U fastapi[all]
pip3 install PyPDF2
```

## Additional Packages to Install

- Docker Containerization

## Ideas

- Docker containerization implementation
- Modularize code and explore GitHub repositories for collaboration
- Enhance error handling for datetime objects

## Running

### Setting Up

#### First Terminal:

```bash
ngrok http 8000
```

Copy the ngrok URL to replace in the `allow_origins` field in `app.py`.

#### Second Terminal:

```bash
uvicorn app:app --reload --workers 1 --host 0.0.0.0 --port 8000
```

Update frontend URLs accordingly.

## Learnings

- Error Handling: Resolve issues with datetime object serialization for JSON.

## Endpoints

- `/get_excel_data/{file_id}`
- `/get_excel_data_biomarkerslist/{file_id}/{count}`
- `/get_excel_data_biomarkers/{file_id}`
- `/get_biomarker_info/{file_id}/{biomarker_name}`
- `/generate_text/{file_id}/{queryprompt}`

### Modifications

1. Customer details endpoint refinement.
2. Simplify horizontal bar details: display only three levels (below, safe, above-Red).
3. Improve Graph detail delivery.
4. Add Diet and Exercise functionalities to OpenAI AI.
5. Git-related enhancements.
