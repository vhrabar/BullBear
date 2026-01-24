import React from 'react';
import { useNavigate } from 'react-router-dom';

const SubscriptionCancel: React.FC = () => {
    const navigate = useNavigate();
    return (
        <div style={{ padding: 20 }}>
            <h2>Subscription canceled</h2>
            <p>Your payment was canceled or not completed. You can try again from your profile or the subscription page.</p>
            <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => navigate('/subscription')}>Try again</button>
                <button onClick={() => navigate('/profile')}>Go to profile</button>
            </div>
        </div>
    );
};

export default SubscriptionCancel;

