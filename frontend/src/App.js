import React from 'react'
import PatientsListComponent from './components/PatientListComponent'
import HeaderComponent from './components/HeaderComponent'
import FooterComponent from './components/FooterComponent'
import { BrowserRouter,Routes, Route } from 'react-router-dom'
import CreatePatientComponent from './components/CreatePatientComponent'
import PatientDetailsComponent from './components/PatientDetailsComponent';

function App() {
  return (
    <div>
      <HeaderComponent/>

      <BrowserRouter>
        <div className='container'>
          <Routes>
            <Route exact path='' element={<PatientsListComponent/>}></Route>
            <Route path='/patients' element={<PatientsListComponent/>}></Route>
            <Route path='/add-patient' element={<CreatePatientComponent/>}></Route>
            <Route path="/patient-details/:patient_id" element={<PatientDetailsComponent />} />
            
        </Routes>
        </div>
      </BrowserRouter>
      
      <FooterComponent/>
    </div>
  )
}

export default App
