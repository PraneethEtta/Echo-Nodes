import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import PatientService from "../services/PatientService";

function CreatePatientComponent() {
  let navigate = useNavigate();

  const [patient, setPatient] = useState({
    name:"",
    patient_id: "",  // Default empty string
    blob_file: "",   // Will store base64 string
    file_name: ""    // Stores file name separately
  });
  const [isLoading, setIsLoading] = useState(false);

  const cancelHandle = (e) => {
    e.preventDefault();
    navigate("/patients");
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPatient({ ...patient, [name]: value });
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setPatient({
        ...patient,
        blob_file: file, // Store file directly
        file_name: file.name
      });
    }
  };
  
  const saveHandle = async (event) => {
    event.preventDefault();
    setIsLoading(true);
  
    if (!patient.patient_id || !patient.blob_file) {
      alert("Please fill in all fields and select a file.");
      return;
    }
  
    // Create FormData object
    const formData = new FormData();
    formData.append("name", patient.name);
    formData.append("patient_id", patient.patient_id);
    formData.append("file", patient.blob_file);
  
    try {
      await PatientService.addPatient(formData);
      navigate("/patients");
    } catch (error) {
      console.error("Error adding patient:", error);
      alert("There was an error adding the patient.");
    }
    setIsLoading(false);
  };
  

  return (
    <div className="container">
      <div className="row mt-3">
        <div className="col-6 offset-md-3">
          <div className="card p-5">
            <h3 className="text-center">Add Patient</h3>
            <form>
              <div className="form-group">
                <label className="my-3" htmlFor="patient_id">
                  Patient Id
                </label>
                <input
                  type="text"
                  name="patient_id"
                  id="patient_id"
                  className="form-control"
                  value={patient.patient_id}
                  onChange={handleChange}
                />
                <label className="my-3" htmlFor="patient_id">
                  Patient Name
                </label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  className="form-control"
                  value={patient.name}
                  onChange={handleChange}
                />
                <label className="my-3" htmlFor="blob_file">
                  Record File:
                </label>
                <input
                  type="file"
                  name="blob_file"
                  id="blob_file"
                  accept="audio/*"
                  className="form-control"
                  onChange={handleFileChange}
                />
                <div className="mt-3">
                  {isLoading ? (
                    <button className="btn btn-secondary" disabled>
                      Submitting...
                    </button>
                  ) : (
                    <>
                      <button className="mt-3 btn btn-danger" onClick={cancelHandle}>
                        Cancel
                      </button>
                      <button className="mt-3 btn btn-success ms-3" onClick={saveHandle}>
                        Submit
                      </button>
                    </>
                  )}
                </div>
              </div>
            </form>
            {isLoading && <div className="mt-3">Loading...</div>} {/* Loading Indicator */}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CreatePatientComponent;
