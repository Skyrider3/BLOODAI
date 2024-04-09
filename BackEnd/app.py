import os, json
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
from typing import Optional, Dict, Any
from biomarker_reference_values import get_reference_values, get_reference_values_barplot, biomarker_LowHigh_range_values


app = FastAPI()

### Add security related keys in env_setup.py


# Retrieve the value of SECRET_KEY environment variable
secret_key = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
client = os.environ.get("client")

# Excel description 
fixed_columns = ["Category", "Biomarker", "UOM", "Low_Range", "High_Range"]

# CORS settings to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://e4b7-2601-19b-b00-26d0-c074-ee5f-1507-15f3.ngrok-free.app","*"],# "*" allow any connections from outside #"2601:44:401:e869:885a:6846:8594:f0c7:0","2601:19b:b00:26d0:98e3:e30d:1202:c711","https://76.98.75.253:3000"],  # Adjust this based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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
from typing import Optional

class ExcelDataRow(BaseModel):
    Category: str = None
    Biomarker: str = None
    UOM: str = None
    Low_Range: float = None
    High_Range: float = None
    additional_columns: Dict[str, Any] = {}


# Define a Pydantic model for the overall response
class ExcelDataResponse(BaseModel):
    data: list[ExcelDataRow]


#experiment  -- page2 for next and prev functionality
#divide the list of biomarkers in sets of 9 -- done
#send only the biomarkers that are requested by page2  ---done
@app.get("/get_excel_data_biomarkerslist/{file_id}/{count}")
async def get_excel_data(file_id: int, count: int):
    db = SessionLocal()

    try:
        # print("ok")
        # Retrieve file data from the database
        excel_file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="File not found")

        # Parse Excel file data as bytes
        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)

        # Process the Excel data using pandas
        df = pd.read_excel(excel_data)
        list_of_biomarkers = list(df["Biomarker"])

         # Split the list into parts
        biomarker_list = [list_of_biomarkers[i:i+9] for i in range(0, len(list_of_biomarkers), 9)]
        #print(biomarker_list)
        # Check if the count is within the range of biomarker_list
        if count < 0 or count > len(biomarker_list):
            raise HTTPException(status_code=400, detail="Invalid count")

        selected_biomarkers = biomarker_list[count]

        #print(len(list_of_biomarkers))
        # # Convert DataFrame to JSON
        json_content = json.loads(df.to_json(orient="records"))
        
        # Process json content and send data to frontend
        response_data = []
        for row in json_content:
            if row["Biomarker"] in selected_biomarkers :
                response_dict = {
                    "name": row["Biomarker"],
                    "value": row["22-7-2022"],  # Example value, replace with desired value ##### make this value passed from endpoint so that you can choose the date from UI
                    "units": row["UOM"],
                    # "first": True, Not needed since it's not being used to reference the value
                    "referenceValues": get_reference_values_barplot(row["Biomarker"])  # Get reference values dynamically
                }
                response_data.append(response_dict)

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()



#### write an another function which calles this function "get_excel_data()" and use this "response_model" to format the json data to the front end.

### - PAGE 3 SENDING THE LIST OF BIOMARKERS TO THE FROTNEND, AND The values for the bar(low, high and the value)
@app.get("/get_excel_data_biomarkers/{file_id}")
async def get_biomarkers(file_id: int) :
    db = SessionLocal()
    try:
        excel_file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="File not found")

            # Parse Excel file data as bytes
        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)

            # Process the Excel data using pandas
        df = pd.read_excel(excel_data)
        biomarkers = df["Biomarker"].tolist()
        # return biomarkers
    
        # # return list(df["Biomarker"])
                # Convert the biomarkers list to JSON format
        biomarkers_convert_json = json.dumps(biomarkers)
        # Parse the JSON string
        biomarkers_json = json.loads(biomarkers_convert_json)
        return biomarkers_json
    
    finally:
        db.close()

#### need to send data in json list 





##page3 dynamic part of it 
# Sample data for reference values (you can replace this with your actual data) --------------fill this
@app.get("/get_biomarker_info/{file_id}/{biomarker_name}")
async def get_biomarker_info(file_id: int, biomarker_name: str):
    db = SessionLocal()
    # Check if the biomarker exists in the reference values
    try:
        # Retrieve file data from the database
        excel_file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="File not found")

        # Parse Excel file data as bytes
        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)

        # Process the Excel data using pandas
        df = pd.read_excel(excel_data)

        # Find the row corresponding to the biomarker
        biomarker_row = df[df["Biomarker"] == biomarker_name]

        # Extract the value of the biomarker from the "22-7-2022" column
        biomarker_value = biomarker_row["22-7-2022"].values[0]  # Assuming there is only one value for the biomarker ------------> need to check
        
        reference_values = biomarker_LowHigh_range_values()

        if biomarker_name not in reference_values:
            raise HTTPException(status_code=404, detail="Biomarker not found")

        # Retrieve reference values for the biomarker
        biomarker_info = reference_values[biomarker_name]


        # Construct response data
        response_data = {
            "biomarker_name": biomarker_name,
            "normal_range": biomarker_info["normal_range"],
            "units": biomarker_info["units"],
            "value": biomarker_value,
            "referenceValues":  get_reference_values(biomarker_name)

            # Add other relevant information about the biomarker here
        }

        return response_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
   


@app.get("/get_excel_data_LineChart/{file_id}/{biomarker}")
async def get_excel_data_LineChart(file_id: int, biomarker : str):
    '''
        This Function is for the sending the specific biomarker value with respective dates, data used for graph plot 
    '''
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

        varying_columns_in_uploaded_excel = [col for col in df.columns if col not in fixed_columns]

        graph_data ={}
        list_dates = []
        list_values = []
        for i in varying_columns_in_uploaded_excel:
            biomarker_date = i
            biomarker_value = df.loc[df['Biomarker'] == biomarker, i].iloc[0]
            # print(type(biomarker_date))
            # print(type(biomarker_value))
            list_dates.append(biomarker_date)
            list_values.append(biomarker_value)
            #graph_data[biomarker_date] =  biomarker_value
        graph_data["date"] = list_dates
        graph_data["values"] = list_values
        
        return graph_data
        #return graph_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


##page-4
# Step 3: OpenAI API Functionality
OPENAI_API_KEY = "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"  # Replace with your OpenAI API key#
openai.api_key = OPENAI_API_KEY


class HealthRecommendations(BaseModel):
    recommendations: dict



def parse_recommendations(recommendations_text):
    recommendations = {}
    sections = recommendations_text.split('\n\n')[1:]  # Exclude the introductory part
    for section in sections:
        if section:
            lines = section.split('\n')
            category = lines[0].strip()
            biomarkers = {}
            biomarkers_list_content = []
            for line in lines[1:]:
                if line:
                    parts = line.split(':')
                    biomarker = parts[0].strip()
                    value = ':'.join(parts[1:]).strip()
                    biomarkers[biomarker] = value
                    #print(biomarkers)
            recommendations[category] = biomarkers
    return recommendations


#recommendations_text = "Based on the given health data, it is difficult to provide a comprehensive analysis of how you are doing without additional information such as your personal health history, lifestyle factors, and any specific health concerns or goals you may have. However, here are a few general observations:\n\n1. Endurance Biomarkers: Your ferritin levels are within the normal range, indicating adequate iron stores. Hematocrit, mean corpuscular volume, and platelet levels are also within normal ranges. These biomarkers suggest that your endurance-related blood parameters are within healthy limits.\n\n2. Heart Biomarkers: Your cholesterol levels are within the normal range, with LDL cholesterol slightly elevated. Triglyceride levels are also within normal limits. HDL cholesterol levels are slightly lower than the recommended range. Overall, your heart-related biomarkers indicate a relatively healthy cardiovascular profile.\n\n3. Inflammation Biomarkers: Most of your inflammation-related biomarkers are within normal ranges, including basophil, eosinophil, lymphocyte, monocyte, neutrophil, and white blood cell counts. However, it is important to note that these biomarkers can vary depending on the presence of any underlying health conditions or recent infections.\n\n4. Metabolism Biomarkers: Your ALT levels are within the normal range, indicating normal liver function. Glucose levels are also within the normal range. Hemoglobin A1C levels are slightly elevated, suggesting a potential risk for diabetes or prediabetes. It is advisable to monitor these levels and consult with a healthcare professional for further evaluation.\n\n5. Recovery Biomarkers: Your albumin levels are within the normal range, indicating normal protein status. AST levels are slightly elevated, which may indicate liver or muscle damage. Potassium and sodium levels are within normal limits. It is recommended to consult with a healthcare professional for further evaluation and interpretation of these biomarkers.\n\n6. TBD Biomarkers: The biomarkers listed under the \"TBD\" category require further information or context to provide a meaningful analysis.\n\nPlease note that this analysis is based solely on the provided biomarker data and does not substitute for a comprehensive medical evaluation. It is always recommended to consult with a healthcare professional for a personalized analysis of your health status."


#recommendations = parse_recommendations(recommendations_text)

# # # Convert recommendations to JSON array
# recommendations_json = json.dumps(recommendations)

# print(recommendations_json)



@app.get("/generate_text/{file_id}/{queryprompt}")#, response_model=HealthRecommendations) ## prompts are "healthdatarecommendations" , "fooddietprecautions" and other one to get doctors list which we need to implement 
async def generate_text(file_id: int, queryprompt : str):
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
        # print(queryprompt)
        # gpt_query = prompt + " from this given health data, give me recommendations"
        if queryprompt == "healthdatarecommendations" : 
            gpt_query = prompt + " from this given health data, give me analysis on how i am doing "
        elif  queryprompt == "fooddietprecautions":
            gpt_query = prompt + " from this given health data, give me recommendations on what food to eat and dietry precautions to take"

        # client = OpenAI(api_key="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")

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

        # lines = recommendations_text.split('\n')
        # print(lines)

        for line in recommendations_text.split('\n'):
            if line.startswith(str(current_category)):
                current_category = line.split('.', 1)[1].strip()
            elif line.strip() and line[0].isdigit():
                if '-' in line:
                    key, value = line.split('-', 1)
                    key = key.strip()
                    value = value.strip()
                    key_value_pairs[current_category] = key_value_pairs.get(current_category, []) + [(key, value)]

        # # Convert the key-value pairs into a dictionary
        # recommendations_dict = {"recommendations": key_value_pairs}
        # print(recommendations_dict)
      
        recommendations = parse_recommendations(recommendations_text)
        #print(recommendations)
        recommendations_content_list = []
        for i in recommendations.keys():
            recommendations_content_list.append(i)

        # print(recommendations_content_list)  
        # # # recommendations_list = list(recommendations_filtered_data)
        # recommendations_json = json.dumps(recommendations_content_list)
        
        # print( recommendations_json)

        return recommendations_content_list[:-1]
        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

#Gemma7B
#key = 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

import requests

@app.get("/generate_text/1/{file_id}/{queryprompt}")
async def generate_text(file_id: int, queryprompt: str):
    '''
    This Function is used for sending the openai Health Report data to the front end
    '''
    db = SessionLocal()

    try:
        excel_file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="File not found")

        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)
        df = pd.read_excel(excel_data)

        prompt = df[["Category", "Biomarker", "22-03-2018"]].to_string(index=False)
        if queryprompt == "healthdatarecommendations":
            # gpt_query = " how are you ? "
            gpt_query = prompt + " from this given health data, give me analysis on how i am doing "
        elif queryprompt == "fooddietprecautions":
            gpt_query = prompt + " from this given health data, give me recommendations on what food to eat and dietary precautions to take"

        invoke_url = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/1361fa56-61d7-4a12-af32-69a3825746fa"

        headers = {
            "Authorization": "Bearer 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",
            "accept": "text/event-stream",
            "content-type": "application/json",
        }

        payload = {
            "messages": [{"content": gpt_query, "role": "user"}],
            "temperature": 0.2,
            "top_p": 0.7,
            "max_tokens": 1024,
            "seed": 42,
            "stream": True
        }

        response = requests.post(invoke_url, headers=headers, json=payload)

        for line in response.iter_lines():
            if line:
                print(line.decode("utf-8"))

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "choices" in data and data["choices"]:
                    response_content = data["choices"][0]["delta"]["content"]
                    print(response_content)
        
    except Exception as e:
        # Handle any other exception (e.g., network error, JSON decode error, etc.)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get('/generate_content/{file_id}/{biomarker}/{query}')
async def generate_biomarker_content(file_id: int, biomarker: str, query: str):
    '''
    This Function is for a Gemma Model health report
    '''
    db = SessionLocal()

    try:
        excel_file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="File not found")

        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)
        df = pd.read_excel(excel_data)
        biomarker_value = df.loc[df['Biomarker'] == biomarker, '22-03-2018'].iloc[0]
        print(biomarker_value)
        biomarker_metric = df.loc[df['Biomarker'] == biomarker, 'UOM'].iloc[0]
        biomarker_low_range = df.loc[df['Biomarker'] == biomarker, 'Low_Range'].iloc[0]
        biomarker_high_range = df.loc[df['Biomarker'] == biomarker, 'High_Range'].iloc[0]
        # prompt_details = df[["Category", "Biomarker", "22-03-2018"]].to_string(index=False)    
        # gpt_query_prompt = ""

        if query == "about":
            gpt_query_prompt = "Give me one line summary of this biomarker " + biomarker
        elif query == "possible_root_cause":
            gpt_query_prompt = " give me the possible root cause of the deficiency in 2 sentences if the value is out of range for "+ biomarker + "the value of the biomarker we have is " + str(biomarker_value) + str(biomarker_metric) + "the low range value is " + str(biomarker_low_range) +  "the low range value is " + str(biomarker_high_range)

        
        def send_openai_request(gpt_query):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-16k-0613",
                messages=[{"role": "user", "content": gpt_query}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
            
        biomarker_content = send_openai_request(gpt_query_prompt)
        return biomarker_content
    

    except Exception as e:
        # Handle any other exception (e.g., network error, JSON decode error, etc.)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

## Adding additional Functionalities

if __name__ == "__main__":
    uvicorn.run('app:app', host="localhost", port=8080, reload=True)