import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import ProtectedRoute from '../auth/AuthProtection';
import { fetchPackages, startStripeCheckout, createPayPalOrder, capturePayPalOrder, SubscriptionPackage } from '../api/payment';

const SubscriptionPage: React.FC = () => {
    const [packages, setPackages] = useState<SubscriptionPackage[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [purchaseLoading, setPurchaseLoading] = useState(false);
    const [purchaseMessage, setPurchaseMessage] = useState<string | null>(null);

    useEffect(() => {
        let mounted = true;
        setLoading(true);
        fetchPackages()
            .then((pkgs) => mounted && setPackages(pkgs))
            .catch((e) => mounted && setError(e?.message || String(e)))
            .finally(() => mounted && setLoading(false));
        return () => { mounted = false; };
    }, []);

    async function buyWithStripe(subscription_type_id: number) {
        setPurchaseLoading(true);
        setPurchaseMessage(null);
        try {
            const res = await startStripeCheckout(subscription_type_id);
            if (res.checkout_url) {
                window.location.href = res.checkout_url;
            } else {
                setPurchaseMessage('Unable to start Stripe checkout.');
            }
        } catch (e: any) {
            setPurchaseMessage(e?.message || String(e));
        } finally {
            setPurchaseLoading(false);
        }
    }

    async function buyWithPayPal(subscription_type_id: number) {
        setPurchaseLoading(true);
        setPurchaseMessage(null);
        try {
            const create = await createPayPalOrder(subscription_type_id);
            const orderId = create.order_id || create.id || null;
            if (!orderId) {
                setPurchaseMessage('Unable to create PayPal order.');
            } else {
                await capturePayPalOrder(orderId, subscription_type_id);
                setPurchaseMessage('PayPal payment captured. Subscription should be active.');
            }
        } catch (e: any) {
            setPurchaseMessage(e?.message || String(e));
        } finally {
            setPurchaseLoading(false);
        }
    }

    return (
        <div className="subscription-page">
            <h2>Subscription plans</h2>
            {loading && <div>Loading plans...</div>}
            {error && <div className="error">Error: {error}</div>}

            {!loading && !error && (
                <div className="packages-list">
                    {packages.length === 0 && <div>No packages available.</div>}
                    {packages.map((pkg) => (
                        <div key={pkg.package_id} className="package-card">
                            <div style={{ fontWeight: 800 }}>{pkg.subscription_type.name} — €{pkg.price}</div>
                            <div style={{ color: '#9ca3af' }}>{pkg.subscription_type.description}</div>
                            <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                                <button onClick={() => buyWithStripe(pkg.subscription_type.id)} disabled={purchaseLoading} className="btn">Buy with Card (Stripe)</button>
                                <button onClick={() => buyWithPayPal(pkg.subscription_type.id)} disabled={purchaseLoading} className="btn">Pay with PayPal</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {purchaseMessage && <div style={{ marginTop: 8 }}>{purchaseMessage}</div>}
        </div>
    );
};

export default function WrappedSubscription() {
    return (
        <ProtectedRoute>
            <Layout>
                <SubscriptionPage />
            </Layout>
        </ProtectedRoute>
    );
}

