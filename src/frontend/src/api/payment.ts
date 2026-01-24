import { getCSRFToken } from "../utils/csrf";

export type SubscriptionPackage = {
    package_id: number;
    price: string;
    subscription_type: {
        id: number;
        name: string;
        description: string;
        price: string;
        duration_days: number;
    };
};

export async function fetchPackages(): Promise<SubscriptionPackage[]> {
    const r = await fetch('/api/payment/packages/', { credentials: 'include' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    // eslint-disable-next-line no-console
    console.debug('fetchPackages raw response:', data);

    // Support both response shapes: { packages: [...] } and direct array [...]
    if (Array.isArray(data)) return data as SubscriptionPackage[];
    return (data && Array.isArray(data.packages)) ? data.packages as SubscriptionPackage[] : [];
}

export async function startStripeCheckout(subscription_type_id: number) {
    const token = getCSRFToken();
    const r = await fetch('/api/payment/stripe/checkout/', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'X-CSRFToken': token } : {}),
        },
        body: JSON.stringify({ subscription_type_id }),
    });
    if (!r.ok) {
        const text = await r.text();
        throw new Error(text || `HTTP ${r.status}`);
    }
    return r.json();
}

export async function createPayPalOrder(subscription_type_id: number) {
    const token = getCSRFToken();
    const r = await fetch('/api/payment/paypal/create/', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'X-CSRFToken': token } : {}),
        },
        body: JSON.stringify({ subscription_type_id }),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
}

export async function capturePayPalOrder(order_id: string, subscription_type_id: number) {
    const token = getCSRFToken();
    const r = await fetch('/api/payment/paypal/capture/', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'X-CSRFToken': token } : {}),
        },
        body: JSON.stringify({ order_id, subscription_type_id }),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
}
