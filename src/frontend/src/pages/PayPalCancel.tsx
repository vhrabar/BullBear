import React from 'react';
import { useNavigate } from 'react-router-dom';

const PayPalCancel: React.FC = () => {
    const navigate = useNavigate();
    return (
        <div style={{ padding: 20 }}>
            <h2>PayPal payment cancelled</h2>
            <p>The PayPal flow was cancelled. You may try again or choose another payment method.</p>
            <button onClick={() => navigate('/subscription')}>Back to subscriptions</button>
        </div>
    );
};

export default PayPalCancel;
