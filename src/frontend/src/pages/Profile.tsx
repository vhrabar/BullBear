import React, { useEffect, useState } from "react";
import { fetchMyProfile, updateMyProfile, UserProfile } from "../api/user";
import "../styles/Profile.css";
import { fetchPackages, startStripeCheckout, createPayPalOrder, capturePayPalOrder, SubscriptionPackage } from "../api/payment";

const ProfilePage: React.FC = () => {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);

    const [packages, setPackages] = useState<SubscriptionPackage[]>([]);
    const [packagesLoading, setPackagesLoading] = useState(false);
    const [packagesError, setPackagesError] = useState<string | null>(null);
    const [purchaseLoading, setPurchaseLoading] = useState(false);
    const [purchaseMessage, setPurchaseMessage] = useState<string | null>(null);

    useEffect(() => {
        let mounted = true;
        setLoading(true);
        fetchMyProfile()
            .then((p) => {
                if (!mounted) return;
                setProfile(p);
            })
            .catch((e) => setError(e.message || String(e)))
            .finally(() => mounted && setLoading(false));

        // fetch packages
        setPackagesLoading(true);
        fetchPackages()
            .then((pkgs) => {
                if (mounted) setPackages(pkgs);
            })
            .catch((e: any) => {
                if (mounted) setPackagesError(e?.message || String(e));
            })
            .finally(() => mounted && setPackagesLoading(false));

        return () => {
            mounted = false;
        };
    }, []);

    const onChange = (field: keyof UserProfile, value: any) => {
        setProfile((p) => (p ? { ...p, [field]: value } : p));
    };

    const onSave = async () => {
        if (!profile) return;
        setSaving(true);
        setError(null);
        try {
            const payload: any = {
                bio: profile.bio,
                avatar_url: profile.avatar_url,
            };
            await updateMyProfile(payload);
            // reload profile
            const updated = await fetchMyProfile();
            setProfile(updated);
        } catch (e: any) {
            setError(e.message || String(e));
        } finally {
            setSaving(false);
        }
    };

    async function buyWithStripe(subscription_type_id: number) {
        setPurchaseLoading(true);
        setPurchaseMessage(null);
        try {
            const res = await startStripeCheckout(subscription_type_id);
            if (res.checkout_url) {
                window.location.href = res.checkout_url; // redirect to Stripe hosted checkout
            } else {
                setPurchaseMessage("Unable to start Stripe checkout.");
            }
        } catch (e: any) {
            setPurchaseMessage(e.message || String(e));
        } finally {
            setPurchaseLoading(false);
        }
    }

    async function buyWithPayPal(subscription_type_id: number) {
        setPurchaseLoading(true);
        setPurchaseMessage(null);
        try {
            const create = await createPayPalOrder(subscription_type_id);
            // PayPal create order returns the full order object which includes HATEOAS links.
            // The payer must approve the order at the 'approve' link before capture is allowed.
            const order = create;
            const links = order?.links || [];
            const approve = links.find((l: any) => l.rel === 'approve' || l.rel === 'payer-action');
            if (approve && approve.href) {
                // Redirect the browser to PayPal approval page. After approval PayPal will redirect
                // back to your configured return URL — that page should call the capture endpoint.
                window.location.href = approve.href;
                return;
            }

            // Fallback: if there is no approve link, try to derive order id and attempt capture (best-effort)
            const orderId = order?.id || create.order_id || null;
            if (!orderId) {
                setPurchaseMessage('Unable to create PayPal order.');
            } else {
                // Attempt capture as a fallback; typical flows require approval so this may still fail.
                await capturePayPalOrder(orderId, subscription_type_id);
                setPurchaseMessage('PayPal payment captured. Subscription should be active.');
                // refresh profile
                const updated = await fetchMyProfile();
                setProfile(updated);
            }
        } catch (e: any) {
            setPurchaseMessage(e.message || String(e));
        } finally {
            setPurchaseLoading(false);
        }
    }

    if (loading) return <div className="profile-page">Loading...</div>;
    if (error) return <div className="profile-page error">Error: {error}</div>;

    return (
        <div className="profile-page">
            <h2>Your Profile</h2>

            {profile && profile.subscription ? (
                <div className="panel">
                    <h3>Subscription</h3>
                    <p>Plan: {profile.subscription.subscription_type.name}</p>
                    <p>Price: €{profile.subscription.package_price}</p>
                    <p>Ends: {new Date(profile.subscription.end_date).toLocaleString()}</p>
                    <p>Active: {profile.subscription.is_active ? "Yes" : "No"}</p>

                    <div style={{ marginTop: 8 }}>
                        <button onClick={() => buyWithStripe(profile.subscription!.subscription_type.id)} disabled={purchaseLoading} className="btn">Extend / Renew with Card</button>
                        <button onClick={() => buyWithPayPal(profile.subscription!.subscription_type.id)} disabled={purchaseLoading} className="btn" style={{ marginLeft: 8 }}>Extend / Renew with PayPal</button>
                    </div>
                </div>
            ) : (
                <div className="panel">
                    <h3>No active subscription</h3>
                </div>
            )}

            <h3>Edit profile</h3>

            {profile ? (
                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        onSave();
                    }}
                >
                    <div>
                        <label>Username:</label>
                        <div>
                            <strong>{(profile as any).username ?? String(profile.user)}</strong>
                        </div>
                    </div>

                    <div>
                        <label>Bio</label>
                        <textarea
                            value={profile.bio || ""}
                            onChange={(e) => onChange("bio", e.target.value)}
                        />
                    </div>

                    <div>
                        <label>Avatar URL</label>
                        <input
                            type="text"
                            value={profile.avatar_url || ""}
                            onChange={(e) => onChange("avatar_url", e.target.value)}
                        />
                    </div>

                    <div style={{ marginTop: 12 }}>
                        <button type="submit" disabled={saving}>
                            {saving ? "Saving..." : "Save"}
                        </button>
                    </div>
                </form>
            ) : (
                <div>No profile found.</div>
            )}

            <div style={{ marginTop: 20 }}>
                <h3>Get a subscription</h3>
                {packagesLoading ? (
                    <div>Loading packages...</div>
                ) : packagesError ? (
                    <div className="error">Error loading packages: {packagesError}</div>
                ) : (
                    <div>
                        {packages.map((pkg) => (
                            <div key={pkg.package_id} style={{ border: '1px solid #334155', padding: 12, borderRadius: 8, marginBottom: 8 }}>
                                <div style={{ fontWeight: 800 }}>{pkg.subscription_type.name} — €{pkg.price}</div>
                                <div style={{ color: '#9ca3af' }}>{pkg.subscription_type.description}</div>
                                <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                                    <button onClick={() => buyWithStripe(pkg.subscription_type.id)} disabled={purchaseLoading} className="btn buy">Buy with Card (Stripe)</button>
                                    <button onClick={() => buyWithPayPal(pkg.subscription_type.id)} disabled={purchaseLoading} className="btn">Pay with PayPal</button>
                                </div>
                            </div>
                        ))}
                        {packages.length === 0 && <div>No packages available.</div>}
                    </div>
                )}
                {purchaseMessage && <div style={{ marginTop: 8 }}>{purchaseMessage}</div>}
            </div>
        </div>
    );
};

export default ProfilePage;
