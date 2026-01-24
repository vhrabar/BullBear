import React from 'react';
import { useNavigate } from 'react-router-dom';

const SubscriptionSuccess: React.FC = () => {
    const navigate = useNavigate();
    return (
        <div style={{ padding: 20 }}>
            <h2>Subscription successful</h2>
            <p>Thank you — your subscription was processed. You can now continue using the platform.</p>
            <button onClick={() => navigate('/profile')}>Go to profile</button>
        </div>
    );
};

export default SubscriptionSuccess;

