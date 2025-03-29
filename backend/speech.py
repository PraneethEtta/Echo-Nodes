import azure.cognitiveservices.speech as speechsdk
import os
import threading
from dotenv import load_dotenv  # Load .env file
import json
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
# import openai
import pyodbc
# from trtr import convo
# from hii import graph
 
 
# Global counters for ID tracking
PATIENT_ID = 1  # Start from P3 since P1 and P2 already exist
PROBLEM_ID = 1
CAUSE_ID = 1
VISIT_ID = 1
 
# Load environment variables from .env file
load_dotenv()
 
conn_str = (
)
 
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_REGION")
 
# Initialize Neo4j connection
graph = Neo4jGraph()
 
# Initialize Azure OpenAI Chat Model
llm = AzureChatOpenAI(
# Azure OpenAI API Configuration
 
)
 
 
def execute_cypher_queries(queries: list):
    """
    Executes a list of Cypher queries on the Neo4j database.
    """
    for query in queries:
        print(f"Executing Query: {query}")
        graph.query(query)
 
 
def generate_cypher_from_conversation(conversation: str,patient_name: str,Visited_date: str) -> list:
    """
    Uses GPT-4o to generate Neo4j Cypher queries dynamically based on patient conversation.
    """
    global PATIENT_ID, PROBLEM_ID, CAUSE_ID, VISIT_ID
 
 
    # Query to fetch existing patient information
    query = f"""
    MATCH (p:Patient {{id: '{PATIENT_ID}'}})-[r1:HAS_PROBLEM]->(pr:Problem)
    OPTIONAL MATCH (pr)-[r2:HAS_CAUSE]->(c:Cause)
    OPTIONAL MATCH (p)-[r3:VISITED_ON]->(v:Visit)
    OPTIONAL MATCH (v)-[r4:FOR_PROBLEM]->(pr2:Problem)
    RETURN p, r1, pr, r2, c, r3, v, r4, pr2
    """
    result = graph.query(query)
 
    # Prompt to guide LLM to generate Cypher queries
    prompt = f"""
    You are an AI assistant that converts patient-doctor conversations into structured Neo4j Cypher queries.
    The Neo4j database has the following schema:
    - (Patient) → [:HAS_PROBLEM] → (Problem)
    - (Problem) → [:HAS_CAUSE] → (Cause)
    - (Patient) → [:VISITED_ON] → (Visit)
    - (Visit) → [:FOR_PROBLEM] → (Problem)
 
    Every entity has a dynamically incremented ID (e.g., '{PATIENT_ID}', 'PR{PROBLEM_ID}', etc.).
 
    Given the following conversation:
    {conversation}
 
    Given The Patient Nmae:-
    {patient_name}
 
    Given The Patient Visited Date:-
    {Visited_date}
 
 
    The existing database information for this patient:
    {result}
 
    --Analyze the conversation carefully. If the patient already has a recorded problem, update the problem details if necessary.
    Identify new problems or causes that are not in the existing data and generate only the necessary Cypher queries to insert new information.
 
    If the patient does not exist, create all relevant nodes and relationships.
    If a new visit is recorded, ensure it is linked correctly to the appropriate problem.
 
    Analyze the existing patient records retrieved from the database. If the patient already exists, compare the new conversation data with the existing records. Identify any new problems, causes, or visits that are not already recorded, and generate Cypher queries only for the new information. Ensure no duplicate entries. If the patient does not exist in the database, create all necessary nodes and relationships from scratch.
 
    --Analyze the conversation carefully. Identify all possible causes of the problem based on the patient's symptoms and history.
    Map these findings to the Neo4j database by generating appropriate Cypher queries.
 
    --Do mappings or relationships correctly okay dont create any duplicates do relationships or mappings correctly in understandable format  
 
    Generate Cypher queries to:
    1. Create a new Patient node (id='{PATIENT_ID}')
    2. Create a Problem node (id='PR{PROBLEM_ID}')
    3. Create one or more Cause nodes (id='C{CAUSE_ID}', 'C{CAUSE_ID + 1}', etc.)
    4. Create a Visit node (id='V{VISIT_ID}')
    5. Establish appropriate relationships.
   
    Only return a JSON array of Cypher queries, like this:
    [
        "CREATE (p:Patient {{id: '{PATIENT_ID}', name: 'John Doe', age: 45, gender: 'Female'}})",
        "CREATE (pr:Problem {{id: 'PR{PROBLEM_ID}', name: 'Skin Rash', description: 'Red, swollen rash on right ankle'}})",
        "CREATE (c1:Cause {{id: 'C{CAUSE_ID}', description: 'Diabetes-related skin issue'}})",
        "CREATE (c2:Cause {{id: 'C{CAUSE_ID + 1}', description: 'Poor sugar control'}})",
        "CREATE (v:Visit {{id: 'V{VISIT_ID}', date: '2025-03-22'}})",
        "MATCH (p:Patient {{id: '{PATIENT_ID}'}}), (pr:Problem {{id: 'PR{PROBLEM_ID}'}}) CREATE (p)-[:HAS_PROBLEM]->(pr)",
        "MATCH (pr:Problem {{id: 'PR{PROBLEM_ID}'}}), (c1:Cause {{id: 'C{CAUSE_ID}'}}) CREATE (pr)-[:HAS_CAUSE]->(c1)",
        "MATCH (pr:Problem {{id: 'PR{PROBLEM_ID}'}}), (c2:Cause {{id: 'C{CAUSE_ID + 1}'}}) CREATE (pr)-[:HAS_CAUSE]->(c2)",
        "MATCH (p:Patient {{id: '{PATIENT_ID}'}}), (v:Visit {{id: 'V{VISIT_ID}'}}) CREATE (p)-[:VISITED_ON]->(v)",
        "MATCH (v:Visit {{id: 'V{VISIT_ID}'}}), (pr:Problem {{id: 'PR{PROBLEM_ID}'}}) CREATE (v)-[:FOR_PROBLEM]->(pr)"
    ]
 
    Your response MUST be a **valid JSON array of Cypher queries ONLY**. Do NOT include explanations or additional text.
 
    """
 
    # Get response from GPT-4o
    response = llm.invoke([HumanMessage(content=prompt)])
    print(response)
    cypher_queries = json.loads(response.content)
 
    # Increment counters for next patient case
    PROBLEM_ID += 1
    CAUSE_ID += len([q for q in cypher_queries if "CREATE (c" in q])  # Increment for multiple causes
    VISIT_ID += 1
    print(PATIENT_ID)
    print(PROBLEM_ID)
    print(CAUSE_ID)
    print(VISIT_ID)
 
    return cypher_queries
 
def transcribe_long_audio(audio_file,uu_id, patient_id, name,file_path, created_at):
    global PATIENT_ID
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
   
    if not os.path.exists(audio_file):
        print("Error: Audio file not found!")
    else:
        print("Audio file found, proceeding with transcription...")
 
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
 
    full_transcript = []
    done = threading.Event()  # Event to detect when transcription is done
 
    def handle_final_result(evt):
        full_transcript.append(evt.result.text)
 
    def stop_transcription(evt):
        """Stops transcription when the session ends"""
        done.set()
 
    speech_recognizer.recognized.connect(handle_final_result)
    speech_recognizer.session_stopped.connect(stop_transcription)
    speech_recognizer.canceled.connect(stop_transcription)
 
    print("Transcribing...")
 
    speech_recognizer.start_continuous_recognition()
    done.wait()  # Wait for transcription to finish
    speech_recognizer.stop_continuous_recognition()
 
    final_text = " ".join(full_transcript)
    print(final_text)
    PATIENT_ID = patient_id
    print(PATIENT_ID)
 
    cypher_queries = generate_cypher_from_conversation(final_text,name,created_at)
    execute_cypher_queries(cypher_queries)
 
    print("\n✅ Data successfully added to Neo4j.")
 
    query = """
        INSERT INTO therapist_patient (id, patient_id, name,blob_file, extracted_convo, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
 
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (uu_id, patient_id, name, file_path, final_text,created_at))
            conn.commit()
 
def stot(uu_id, patient_id, name,file_path, created_at,path):
 
    audio_file = "C:\\Users\\9901063\\Downloads\\Hackathon\\backend\\uploads\\"+path
    transcribe_long_audio(audio_file,uu_id, patient_id, name,file_path, created_at)
 