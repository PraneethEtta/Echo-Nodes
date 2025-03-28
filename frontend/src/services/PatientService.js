import axios from 'axios';

const PATIENT_API = "http://127.0.0.1:8000";

class PatientService {
  // Fetch all patients
  getpatient() {
    return axios.get(`${PATIENT_API}/patients`);
  }
  graph(patient_id) {
    return axios.get(`${PATIENT_API}/generate-graph/${patient_id}`);
}


  // Add a new patient
  addPatient(patient){
    try {
      return axios.post("http://127.0.0.1:8000/add-patient", patient, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
    } 
    catch (error) {
      return ('Error uploading file', error);
    }
  }



}

export default new PatientService();
