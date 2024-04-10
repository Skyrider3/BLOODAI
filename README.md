<<<<<<< HEAD
# BLOODAI

=======
# GPTWrapper
# python3 -m pip install  uvicorn[standard]
# python3 uvicorn main:app --reload
# pip3 install python-multipart
# pip3 install --upgrade openai
# pip3 install -U fastapi[all]
# pip3 install PyPDF2

# Additional Packages to Install - Dept

### Implement Docker Containerization for this 

## Ideas


## running 
# start virtual environment
 
# In 1st termianl run 
### ngrok http 8000
### copy the relevant "https://14fc-2601-19b-b00-26d0-d9f7-d24a-cc11-4eda.ngrok-free.app:3000 "  to the "allow_origins= "https://3eea-2601-19b-b00-26d0-d9f7-d24a-cc11-4eda.ngrok-free.app:3000"... in the app.py



# In second terminal run 
### uvicorn app:app --reload --workers 1 --host 0.0.0.0 --port 8000

# in front end we need to change this 

# "https://e8ff-2601-19b-b00-26d0-bd23-a214-cc68-e5fb.ngrok-free.app" chnage this according to the generated ngrocck service


### check for github repos for modularise code


### Learnings

# error:  {"detail":"datetime.datetime(2018, 3, 22, 0, 0)"} The error you're encountering suggests that there's a datetime object present in your data, which cannot be directly serialized to JSON. To resolve this issue, you need to handle datetime objects appropriately, perhaps by converting them to strings or some other format that can be serialized to JSON. Here's how you can modify your code to handle datetime object

<!-- 
@app.get("/get_excel_data/{file_id}")
@app.get("/get_excel_data_biomarkerslist/{file_id}/{count}")
@app.get("/get_excel_data_biomarkers/{file_id}")
@app.get("/get_biomarker_info/{file_id}/{biomarker_name}")

@app.get("/generate_text/{file_id}/{queryprompt}") -->


### check page 3 value on the horizontal bar part

###### Modifications

# page 1 : Customer details end point
# page 2 : Inncorect horizontal bar details -- we dont need all the reference values, we just need 3 levels [ below , safe , above(Red) ]
# page 3 : Send Graph detail
# page 4 : Add the Diet and Exercise functionalies to OPENAI AI
# page 5 : git 
>>>>>>> master
