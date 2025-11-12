import { useState, useEffect } from 'react';
import './StockView.css';
import Footer from '../components/Footer';
import { Link } from "react-router-dom";


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
    const [content, setContent] = useState<JSX.Element>(<div>Loading...</div>);

    // const API_URL = "http://localhost:8000/api/trading/portfolio-holdings/";
    const API_URL = "/api/trading/portfolio-holdings/"; // provjera proxy servera

    useEffect(() => {
        fetch(API_URL, {
            method: 'GET',
            headers: {
                "Content-Type": "application/json",
            },
             credentials: 'include'
        })
        .then(async (res) => {
            if (!res.ok) {
                throw new Error(`HTTP ${res.status} - ${res.statusText}`);
            }
            return res.json();
        })
        .then((data) => {
            if (!data || data.length === 0) {
                setContent(<div id='empty'>No holdings found.</div>);
                return;
            }

            const list = data.map((x: {
                id: number;
                instrument: string;
                current_value: string;
                profit_loss: string;
                quantity: string;
                average_price: string;
            }) => (
                <tr key={x.id} className="stock-item">
                    <td>
                        <p>{x.instrument.split('(')[0]}</p>
                        <p className='corpo'>{x.instrument.split('(')[1].split(')')[0]}</p>
                    </td>
                    <td>{x.current_value}</td>
                    <td style={(x.profit_loss[0]=='-')? {color: 'red'}:{color: 'green'}}>{x.profit_loss}</td>
                    <td>{x.quantity}</td>
                    <td>{x.average_price}</td>
                </tr>
            ));

            setContent(
            <div id='container-root'>
                <table id='container'>
                    <tr>
                        <th>Instrument</th>
                        <th>Current Value</th>
                        <th>Profit/Loss</th>
                        <th>Quantity</th>
                        <th>Average Price</th>
                    </tr>
                    {list}
                </table>
            </div>);
        })
        .catch((error) => {
            setContent(<div id='error'>Error loading data: {error.message}</div>);
        });
    }, [API_URL]);


    //TEST VERZIJA- DO NOT DELETE!!! --- lakšse za testiranje
    // useEffect(() => {
    //     const list = test.map((x: {
    //             id: number;
    //             instrument: string;
    //             current_value: string;
    //             profit_loss: string;
    //             quantity: string;
    //             average_price: string;
    //         }) => (
    //             <tr key={x.id} className="stock-item">
    //                 <td>
    //                     <p>{x.instrument.split('(')[0]}</p>
    //                     <p className='corpo'>{x.instrument.split('(')[1].split(')')[0]}</p>
    //                 </td>
    //                 <td>{x.current_value}</td>
    //                 <td style={(x.profit_loss[0]=='-')? {color: 'red'}:{color: 'green'}}>{x.profit_loss}</td>
    //                 <td>{x.quantity}</td>
    //                 <td>{x.average_price}</td>
    //             </tr>
    //         ));
    //         setContent(
    //         <div id='container-root'>
    //             <table id='container'>
    //                 <tr>
    //                     <th>Instrument</th>
    //                     <th>Current Value</th>
    //                     <th>Profit/Loss</th>
    //                     <th>Quantity</th>
    //                     <th>Average Price</th>
    //                 </tr>
    //                 {list}
    //             </table>
    //         </div>);
    // }, []);

    return (
        <div>
            <nav className="auth-nav">
                <Link to="/" className="auth-logo">
                    <span className="logo-icon">📈</span>
                    <span className="logo-text">BullBear</span>
                </Link>
            </nav>

            {content}

            <Footer />
        </div>
    );
}

export default StockView;
