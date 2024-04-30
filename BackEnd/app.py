from jose import JWTError, jwt
import os, json
import pandas as pd
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException,Request,Form
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from passlib.context import CryptContext
import fastapi
from io import StringIO,BytesIO 
import openai,json, uvicorn,asyncio
from openai import OpenAI
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from database import get_db, create_tables
from models import UserModel, ExcelFile
from schemas import Token
from pydantic import BaseModel
import uuid
from biomarker_reference_values import get_reference_values, get_reference_values_barplot, biomarker_LowHigh_range_values

app = FastAPI()
create_tables()

# CORS settings to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ea1b-2601-19b-b00-26d0-e534-352a-3e94-e712.ngrok-free.app","*"],# "*" allow any connections from outside #"2601:44:401:e869:885a:6846:8594:f0c7:0","2601:19b:b00:26d0:98e3:e30d:1202:c711","https://76.98.75.253:3000"],  # Adjust this based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Retrieve the value of SECRET_KEY environment variable
# SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"

SECRET_KEY = str(uuid.uuid4())

# client = os.environ.get("client") #cahnge this
client = OpenAI(api_key="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")

ACCESS_TOKEN_EXPIRE_MINUTES = 10000

# @app.get("/generate_content/healthDataRecommendations")
# async def read_root():
#     return {"message": "Hello, this is a test endpoint"}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str, db):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=10000)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)): #= Depends(oauth2_scheme), db=None):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # print("inside the get_current_suer")
    # print(token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print("Algorithm",ALGORITHM)
        # print("Secret",SECRET_KEY)
        print("Payload",payload)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user is None:
        raise credentials_exception
    return user

class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(self, username: str = Form(...), password: str = Form(...), name: str = Form(...)):
        super().__init__(username=username, password=password, scope="")
        self.name = name

@app.post("/api/signup")
async def signup(
    form_data: CustomOAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    print("inside")
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(form_data.password)
    new_user = UserModel(email=form_data.username, password=hashed_password, name=form_data.name)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/api/signin", response_model=Token)
async def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    # print(user.name)
    return {"access_token": access_token, "token_type": "bearer","name": user.name}


class UpdateUserRequest(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str

@app.put("/api/updateuser")
async def update_user_details(request: UpdateUserRequest, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.name = request.name
    current_user.address = request.address
    current_user.city = request.city
    current_user.state = request.state
    current_user.zip_code = request.zip_code
    current_user.country = request.country

    db.commit()
    db.refresh(current_user)

    return {"message": "User details updated successfully"}

# send login user details to the front end

@app.get("/api/user_details")
async def get_user(current_user: UserModel = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email,
        "address": current_user.address,
        "city": current_user.city,
        "state": current_user.state,
        "zip_code": current_user.zip_code,
        "country": current_user.country
    }

# @app.post("/upload_excel") this should be able to save any file into db and foe excel files it should use this "content = file.file.read() db_file = ExcelFile(file_name=file.filename, file_data=content, user=current_user) db.add(db_file) db.commit()"

@app.post("/api/upload_excel")#, response_model=None)
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    print("Inside function")
    try:
        content = file.file.read()
        db_file = ExcelFile(file_name=file.filename, file_data=content, user=current_user)
        db.add(db_file)
        db.commit()

        return JSONResponse(content={"file_id": db_file.id, "message": "File uploaded successfully"}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/get_files")
# async def get_files(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
#     files = db.query(ExcelFile).filter(ExcelFile.user == current_user).all()
#     return {"files": files}

# @app.get("/download_file/{file_id}")
# async def download_file(file_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
#     file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
#     if file is None:
#         raise HTTPException(status_code=404, detail="File not found")
#     if file.user != current_user:
#         raise HTTPException(status_code=403, detail="You are not authorized to download this file")
#     return StreamingResponse(file.file_data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# @app.get("/delete_file/{file_id}")
# async def delete_file(file_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
#     file = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
#     if file is None:
#         raise HTTPException(status_code=404, detail="File not found")
#     if file.user != current_user:
#         raise HTTPException(status_code=403, detail="You are not authorized to delete this file")
#     db.delete(file)
#     db.commit()
#     return {"message": "File deleted successfully"}

# modified page 2 code check this 

@app.get("/get_excel_data_biomarkerslist/{count}")
async def get_excel_data(count: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    try:
        # Retrieve the most recent file for the current user
        excel_file = db.query(ExcelFile).filter(ExcelFile.user_id == current_user.id).order_by(ExcelFile.id.desc()).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="No files found for the user")

        # Parse Excel file data as bytes
        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)

         
        df = pd.read_excel(excel_data)
        list_of_biomarkers = list(df["Biomarker"])

        # Get the name of the last column
        last_column = df.columns[-1]

        # Split the list into parts
        biomarker_list = [list_of_biomarkers[i:i+9] for i in range(0, len(list_of_biomarkers), 9)]

        # Check if the count is within the range of biomarker_list
        if count < 0 or count >= len(biomarker_list):
            raise HTTPException(status_code=400, detail="Invalid count")

        selected_biomarkers = biomarker_list[count]

        # Process json content and send data to frontend
        response_data = []
        for _, row in df.iterrows():
            if row["Biomarker"] in selected_biomarkers:
                response_dict = {
                    "name": row["Biomarker"],
                    "value": row[last_column],  # Fetch the value from the last column
                    "units": row["UOM"],
                    "referenceValues": get_reference_values_barplot(row["Biomarker"])
                }
                response_data.append(response_dict)

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

###List of biomarkers for page 3
@app.get("/get_excel_data_biomarkers")
async def get_biomarkers(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    try:
        # Retrieve the most recent file for the current user
        excel_file = db.query(ExcelFile).filter(ExcelFile.user_id == current_user.id).order_by(ExcelFile.id.desc()).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="No files found for the user")

        # Parse Excel file data as bytes
        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)

         
        df = pd.read_excel(excel_data)
        biomarkers = df["Biomarker"].tolist()

        return biomarkers

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
fixed_columns = ["Category", "Biomarker", "UOM", "Low_Range", "High_Range"]


@app.get('/get_available_dates/dates')
async def get_available_dates(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    try:
        # Retrieve the most recent file for the current user
        excel_file = db.query(ExcelFile).filter(ExcelFile.user_id == current_user.id).order_by(ExcelFile.id.desc()).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="No files found for the user")

        # Parse Excel file data as bytes
        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)

         
        df = pd.read_excel(excel_data)

        # Get the column names excluding the fixed columns
        blood_test_dates = [col for col in df.columns if col not in fixed_columns]

        return blood_test_dates

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Modified code # instead of just numbers this will return list of biomarker values.
@app.get("/get_excel_data_pie/{date}")
async def get_excel_data_pie(date: str, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    '''This function returns the list of biomarkers in below, within, and above range for a specific date, along with their values.'''
    try:
        # Retrieve the most recent file for the current user
        excel_file = db.query(ExcelFile).filter(ExcelFile.user_id == current_user.id).order_by(ExcelFile.id.desc()).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="No files found for the user")

        # Parse Excel file data as bytes
        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)

         
        df = pd.read_excel(excel_data)

        # Create lists to store biomarkers and their values in each range
        below_range_biomarkers = []
        within_range_biomarkers = []
        above_range_biomarkers = []

        # Iterate over each row
        for _, row in df.iterrows():
            biomarker = row['Biomarker']
            biomarker_value = row[date]
            biomarker_low_range = row['Low_Range']
            biomarker_high_range = row['High_Range']

            if pd.isna(biomarker_value) or pd.isna(biomarker_low_range) or pd.isna(biomarker_high_range):
                continue  # Skip rows with missing values

            biomarker_data = {
                'name': biomarker,
                'value': biomarker_value
            }

            if biomarker_value < biomarker_low_range:
                below_range_biomarkers.append(biomarker_data)
            elif biomarker_low_range <= biomarker_value <= biomarker_high_range:
                within_range_biomarkers.append(biomarker_data)
            else:
                above_range_biomarkers.append(biomarker_data)

        # Prepare the response data
        response_data = {
            "below_range_biomarkers": below_range_biomarkers,
            "within_range_biomarkers": within_range_biomarkers,
            "above_range_biomarkers": above_range_biomarkers
        }

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/generate_text/{queryprompt}")
async def generate_text(queryprompt: str, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    try:
        print("inside generate function")
        # Retrieve the most recent file for the current user
        excel_file = db.query(ExcelFile).filter(ExcelFile.user_id == current_user.id).order_by(ExcelFile.id.desc()).first()
        if not excel_file:
            raise HTTPException(status_code=404, detail="No files found for the user")
        print(excel_file)
        # Parse Excel file data as bytes
        content_bytes = excel_file.file_data
        excel_data = BytesIO(content_bytes)
        # print(excel_data)
        df = pd.read_excel(excel_data)
        # print(df)
        prompt = df.to_string()

        if queryprompt == "healthdatarecommendations":
            gpt_query = prompt + " from this given health data, give me analysis on how i am doing "
        elif queryprompt == "fooddietprecautions":
            gpt_query = prompt + " from this given health data, give me recommendations on what food to eat and dietary precautions to take"

        def send_openai_request(gpt_query):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-16k-0613",
                messages=[{"role": "user", "content": gpt_query}],
                temperature=0
            )
            return response.choices[0].message.content.strip()

        recommendations_text = send_openai_request(gpt_query)

        # Parse the OpenAI response to extract key-value pairs
        key_value_pairs = {}
        current_category = None

        for line in recommendations_text.split('\n'):
            if line.startswith(str(current_category)):
                current_category = line.split('.', 1)[1].strip()
            elif line.strip() and line[0].isdigit():
                if '-' in line:
                    key, value = line.split('-', 1)
                    key = key.strip()
                    value = value.strip()
                    key_value_pairs[current_category] = key_value_pairs.get(current_category, []) + [(key, value)]

        recommendations = parse_recommendations(recommendations_text)

        recommendations_content_list = []
        for i in recommendations.keys():
            recommendations_content_list.append(i)

        return recommendations_content_list[:-1]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




## Adding additional Functionalities

# Adding bio marker gap analysis - set of biomarkers tested and set of bio markers not tested : potential biomarkers to test [ map of different biomarkers so that we can see the correlation of one biomarker with the other and recommend the user to get tested for potential biomarker.]

# Adding biomarker risk analysis -- Implenmt knowledge Graph to evaluate and map different biomarker effects and their risk anlysis [ For Initial Phase Map few Biomarkers and their combined risk analysis : either knowledge graph / rag trained on medical documents ]

if __name__ == "__main__":
    uvicorn.run('app:app', host="localhost", port=8080, reload=True)