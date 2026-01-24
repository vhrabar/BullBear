import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { capturePayPalOrder } from '../api/payment';

const PayPalReturn: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [message, setMessage] = useState('Processing PayPal return...');

    useEffect(() => {
        const token = searchParams.get('token') || searchParams.get('orderId') || null;
        const subscription_type_id = Number(searchParams.get('subscription_type_id') || searchParams.get('subscriptionTypeId') || 0);
        if (!token || !subscription_type_id) {
            setMessage('Missing return parameters from PayPal.');
            return;
        }

        (async () => {
            try {
                await capturePayPalOrder(token, subscription_type_id);
                setMessage('Payment captured successfully. Redirecting...');
                setTimeout(() => navigate('/subscription/success'), 1500);
            } catch (e: any) {
                setMessage(e?.message || String(e));
            }
        })();
    }, [searchParams, navigate]);

    return (
        <div style={{ padding: 20 }}>
            <h2>Processing PayPal return</h2>
            <p>{message}</p>
        </div>
    );
};

export default PayPalReturn;

