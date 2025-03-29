import datetime
import uuid
import os
import pyodbc
from fastapi import FastAPI, UploadFile, Form, File
from azure.storage.blob import BlobServiceClient
from fastapi.middleware.cors import CORSMiddleware
from speech_to_text import stot
from hii import graph_router
 
 
app = FastAPI()
 
app.include_router(graph_router)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# 📌 Azure SQL Connection String
conn_str = (
   
)
 
# 📌 Azure Blob Storage Configuration
AZURE_CONNECTION_STRING = ""
CONTAINER_NAME = ""    
 
# 📌 Function to upload file to Azure Blob Storage
LOCAL_STORAGE_DIR = "uploads"
 
# Ensure the directory exists
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)
 
def save_file_locally(filename: str, file_data,uu_id, patient_id,name,created_at) -> str:
    """Saves the uploaded file locally instead of Azure Blob Storage."""
    unique_filename = str({uuid.uuid4()}-{filename})
    file_path = os.path.join(LOCAL_STORAGE_DIR, unique_filename)
   
    with open(file_path, "wb") as local_file:
        local_file.write(file_data.read())  # Read and write file contents
    stot(uu_id, patient_id, name,file_path, created_at,unique_filename)
    return file_path  # Return the local file path
 
@app.post("/add-patient")
async def add_patient(name: str = Form(...),patient_id: str = Form(...), file: UploadFile = File(...)):
    """Handles patient addition and saves file locally instead of Azure Blob Storage."""
    try:
        uu_id = str(uuid.uuid4())
        x = datetime.datetime.now()
        created_at = x.strftime("%Y-%m-%d %H:%M:%S")
        save_file_locally(file.filename, file.file,uu_id, patient_id,name, created_at)  # Save file locally
       
       
 
 
        return {
            "message": "Patient added successfully",
           
            # "file_path": file_path  # Return local file path
        }
    except Exception as e:
        return {"error": str(e)}
   
@app.get("/patients")
def get_patients():
    """Retrieves all patient records from the database."""
    try:
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM [dbo].[therapist_patient]")
                records = cursor.fetchall()
 
                columns = [column[0] for column in cursor.description]
                patients = [dict(zip(columns, row)) for row in records]
 
        return {"patients": patients}
    except Exception as e:
        return {"error": str(e)}