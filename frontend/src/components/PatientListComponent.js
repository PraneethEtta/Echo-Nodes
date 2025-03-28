import React, { Component } from 'react';
import PatientService from '../services/PatientService';
import { Link, useNavigate,withRouter } from 'react-router-dom';
// import { useNavigate } from "react-router-dom";
// import PatientService from "../services/PatientService";

export default class PatientsListComponent extends Component {

    
    constructor(props) {
        super(props);
        // Initialize patients as an empty array
        this.state = {
            patients: [] 
        }
    }

    componentDidMount() {
      PatientService.getpatient().then((res) => {
          console.log("API Response:", res.data); // Check if res.data is an object with patients array
          if (res.data && Array.isArray(res.data.patients)) {
              // Set patients from the API response
              this.setState({ patients: res.data.patients });
          } else {
              console.error("Expected an array of patients, but got:", res.data);
          }
      }).catch(error => {
          console.error("Error fetching patients:", error);
      });
  }
saveHandle = (id) => {
    // Call the graph method on the PatientService with the id
    PatientService.graph(id).then((res) => {
        console.log("Successfully Done"); // Check if res.data is an object with patients array
    }).catch(error => {
        console.error("Error fetching patients:", error);
    });
    const graphUrl = `/${id}.html`;
    window.open(graphUrl, '_blank');

};


  render() {
    return (
        <div className='container mt-3'>
            <h4 className='text-center'>Patient List</h4>
            <div className='row mt-3'>
                <Link to='/add-patient' className='btn btn-outline-primary mb-3'>Add Patient</Link>
                <table className='table table-bordered table-striped'>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>NAME</th>
                            <th>APPOINTMENT DATE</th>
                            <th>DETAILS</th>
                        </tr>
                    </thead>
                    <tbody>
                        {
                            Array.isArray(this.state.patients) && this.state.patients.length > 0 ? (
                                this.state.patients.map((patient) => (
                                    <tr key={patient.id}>
                                        <td>{patient.patient_id}</td>
                                        <td>{patient.name}</td>
                                        <td>{patient.created_at}</td>
                                        <td><button className="mt-3 btn btn-success ms-3" onClick={() => this.saveHandle(patient.patient_id)}>Details</button></td>
                                        </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center">No patients found</td>
                                </tr>
                            )
                        }
                    </tbody>
                </table>
            </div>
        </div>
    );
  }
}
