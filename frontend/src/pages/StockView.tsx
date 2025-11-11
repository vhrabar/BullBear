//import React from "react";
import { useState, useEffect } from 'react';
import './StockView.css';
import Footer from '../components/Footer';
import { Link } from "react-router-dom";

// TEST VALUES
let test = JSON.parse('['+
    '{'+
        '"id": 1,'+
        '"instrument": "AMD (AMD)",'+
        '"current_value": "31014.000",'+
        '"profit_loss": "294.000",'+
        '"quantity": "120.000",'+
        '"average_price": "256.000",'+
        '"added_at": "2025-11-03T16:50:25.5999",'+
        '"portofolio": 1'+
    '},'+
    '{'+
        '"id": 2,'+
        '"instrument": "NVDA(Nvidia Corporation)",'+
        '"current_value": "25721.760",'+
        '"profit_loss": "137.760",'+
        '"quantity": "123.000",'+
        '"average_price": "208.000",'+
        '"added_at": "2025-11-03T16:57:07.7827",'+
        '"portofolio": 1'+
    '}'+
']');

function StockView() {
    const [load, setLoad] = useState(<div>No</div>);


    // GLAVNI DIO: BACKEND INTEGRATION
    // fetch('/api/trading/portfolio-holdings/', {
    //     method : 'GET',
    //     headers : {
    //         "Content-Type": "application/json"
    //     },
    //     body : ""
    // }
    // ).then((res) => {
    //     if (res.ok) {
    //         res.json().then((porto) => {
    //             const list = porto.map((x: { instrument: string; }) => <div>{x.instrument}</div>)
    //             useEffect(() => setLoad(<div id='container'>{list}</div>), []);
    //         });
    //     }
    //     else {
    //         useEffect(() => setLoad(<div id='error'>ERROR:  {res.statusText}  </div>), []);
    //     }
    // });

    //TEST IMPLEMENTATION
    const list = test.map((x: { instrument: string; }) => <div>{x.instrument}</div>)
    useEffect(() => setLoad(<div id='container'>{list}</div>), []);

    return (<div><nav className="auth-nav">
        <Link to="/" className="auth-logo">
          <span className="logo-icon">📈</span>
          <span className="logo-text">BullBear</span>
        </Link>
      </nav>
      {load} 
      <Footer />
      </div>);
};

export default StockView;
