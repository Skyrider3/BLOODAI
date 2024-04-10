
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException,Request,Form
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import openai,json, uvicorn,asyncio
from openai import OpenAI
from pydantic import BaseModel
from PyPDF2 import PdfReader
from io import StringIO,BytesIO 
from datetime import datetime, timedelta
from passlib.hash import bcrypt  # Install passlib with: pip install passlib
import fastapi
# from database import SessionLocal, ExcelFile

app = FastAPI()

# Assuming you have a secret key for JWT signing
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


# CORS settings to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://7405-2601-19b-b00-26d0-78f1-ba66-efe0-7b66.ngrok-free.app\:3000","2601:44:401:6b80:f1ef:bd71:7ac3:957e","https://76.98.74.225:0"],  # Adjust this based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2PasswordBearer for handling token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/hello")
async def read_root():
    return {"message": "Hello, this is a test endpoint new app!"}



DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()


class ExcelFile(Base):
    __tablename__ = "excel_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    file_data = Column(String)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Step 1: Store Excel File in Database

@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    db = SessionLocal()
    try:    
        # Store file in database
        content = file.file.read()
        db_file = ExcelFile(file_name=file.filename, file_data=content)
        db.add(db_file)
        db.commit()

       # Return the generated file ID
        return JSONResponse(content={"file_id": db_file.id, "message": "File uploaded successfully"}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


# # Step 2: Parse Excel File Data and Send to Frontend       

# Define a Pydantic model for an individual row in the response
class ExcelDataRow(BaseModel):
    category: str
    biomarker: str
    uom: str = None
    low_range: float = None
    high_range: float = None
    #values: dict


# Define a Pydantic model for the overall response
class ExcelDataResponse(BaseModel):
    data: list[ExcelDataRow]

# @app.get("/get_excel_data/{file_id}")
@app.get("/get_excel_data/{file_id}")
async def get_excel_data(file_id: int):
    db = SessionLocal()

    try:
        # Retrieve file data from the database
        excel_file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="File not found")

        # Parse Excel file data as bytes
        content_bytes = excel_file.file_data

        # Use BytesIO to create a file-like object
        excel_data = BytesIO(content_bytes)

        # Process the Excel data using pandas
        df = pd.read_excel(excel_data)  # Use read_excel for Excel files
        # print(df)
        
        # Convert DataFrame to JSON
        #json_content = df.to_dict(orient="records", default_handler=str)  # Use default_handler to handle non-serializable values
        json_content = json.loads(df.to_json(orient="records"))
        # print(json_content)

        # # process the Nan values **update this code snippet for handling all null or Nan Values**
        # for row in json_content:
        #     row["Low Range"] = round(pd.to_numeric(row["Low Range"], errors="coerce"),2)
        #     row["High Range"] = round(pd.to_numeric(row["High Range"], errors="coerce"),2)
        #     #row["UOM"] = pd.to_numeric(row["UOM"], errors="coerce") # the metrics are not a numeric ones

        # Process json content  as needed and send data to frontend
        response_model = ExcelDataResponse(
            data=[
                ExcelDataRow(
                    category=row["Category"],
                    biomarker=row["Biomarker"],
                    uom=row["UOM"],
                    low_range=row["Low Range"],
                    high_range=row["High Range"],
                    #values={key: value for key, value in row.items() if key not in ["Category", "Biomarker", "UOM", "Low Range", "High Range"]}
                )
                for row in json_content
            ]
        )
        # Further process the data to the desired format
        formatted_data = []
        for item in response_model.data:
            formatted_item = {
                "name": item.biomarker,
                "desc": item.biomarker.lower(),  # Assuming description is a lowercase version of the biomarker
                "normalRange": [item.low_range, item.high_range],
                "value": None,  # You need to add the actual value from your data
                "units": item.uom,
                "lineValues": [
                    [200, "green"],
                    [279, "yellow"],
                    [315, "red"],
                ]  # You need to customize this based on your data
            }
            formatted_data.append(formatted_item)

        return formatted_data##New code 

        # # # For now, returning the data as JSON
        # return JSONResponse(content=json_content, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

# write an another function whi calles this function "get_excel_data()" and use this "response_model" to format the json data to the front end.

@app.get("/get_excel_data_LineChart/{file_id}")
async def get_excel_data_LineChart(file_id: int):
    data = get_excel_data(file_id)
    print(data)


# Step 3: OpenAI API Functionality
OPENAI_API_KEY = "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"  # Replace with your OpenAI API key
openai.api_key = OPENAI_API_KEY

# @app.get("/generate_text/{file_id}")
# async def generate_text(file_id: int):
#     db = SessionLocal()

#     try:
#         # Retrieve file data from the database
#         excel_file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
#         if not excel_file:
#             raise HTTPException(status_code=404, detail="File not found")

#         # Parse Excel file data as bytes
#         content_bytes = excel_file.file_data

#         # Use BytesIO to create a file-like object
#         excel_data = BytesIO(content_bytes)

#         # Process the Excel data using pandas
#         df = pd.read_excel(excel_data) 

#         # Process df and get text for OpenAI prompt
#         prompt = df.to_string()
#         #print(prompt)
#         gpt_query = prompt + " from this given health data, give me recommendations"

#         client = OpenAI( api_key="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")  


#         def send_openai_request(gpt_query):
#             response = client.chat.completions.create( model="gpt-3.5-turbo-16k-0613", messages=[{"role": "user", "content": gpt_query}],temperature=0)
#             return response.choices[0].message.content.strip()

#         text = send_openai_request(gpt_query)
#         return text

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     finally:
#         db.close()


class HealthRecommendations(BaseModel):
    recommendations: dict

@app.get("/generate_text/{file_id}", response_model=HealthRecommendations)
async def generate_text(file_id: int):
    db = SessionLocal()

    try:
        # Retrieve file data from the database
        excel_file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="File not found")

        # Parse Excel file data as bytes
        content_bytes = excel_file.file_data

        # Use BytesIO to create a file-like object
        excel_data = BytesIO(content_bytes)

        # Process the Excel data using pandas
        df = pd.read_excel(excel_data)

        # Process df and get text for OpenAI prompt
        prompt = df.to_string()
        # gpt_query = prompt + " from this given health data, give me recommendations"
        gpt_query = prompt + " from this given health data, give me recommendations on what food to eat and dietry precautions to take"

        client = OpenAI(api_key="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")

        def send_openai_request(gpt_query):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-16k-0613",
                messages=[{"role": "user", "content": gpt_query}],
                temperature=0
            )
            return response.choices[0].message.content.strip()

        recommendations_text = send_openai_request(gpt_query)
        #print(recommendations_text)
        # Parse the OpenAI response to extract key-value pairs
        key_value_pairs = {}
        current_category = None

        lines = recommendations_text.split('\n')
        print(lines)

        # for line in recommendations_text.split('\n'):
        #     if line.startswith(str(current_category)):
        #         current_category = line.split('.', 1)[1].strip()
        #     elif line.strip() and line[0].isdigit():
        #         if '-' in line:
        #             key, value = line.split('-', 1)
        #             key = key.strip()
        #             value = value.strip()
        #             key_value_pairs[current_category] = key_value_pairs.get(current_category, []) + [(key, value)]

        # # Convert the key-value pairs into a dictionary
        # recommendations_dict = {"recommendations": key_value_pairs}



        return recommendations_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run('app:app', host="localhost", port=8080, reload=True)

