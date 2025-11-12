import { useState, useEffect } from 'react';
import './StockView.css';
import Footer from '../components/Footer';
import { Link } from "react-router-dom";

function StockView() {
    const [content, setContent] = useState<JSX.Element>(<div>Loading...</div>);

    const API_URL = "http://localhost:8000/api/trading/portfolio-holdings/";

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
                <div key={x.id} className="stock-item">
                    <div className="instrument">{x.instrument}</div>
                    <div className="details">
                        <p>Current Value: {x.current_value}</p>
                        <p>Profit/Loss: {x.profit_loss}</p>
                        <p>Quantity: {x.quantity}</p>
                        <p>Average Price: {x.average_price}</p>
                    </div>
                </div>
            ));

            setContent(<div id='container'>{list}</div>);
        })
        .catch((error) => {
            setContent(<div id='error'>Error loading data: {error.message}</div>);
        });
    }, [API_URL]);

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
