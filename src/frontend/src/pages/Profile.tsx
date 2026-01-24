import React, { useEffect, useState } from "react";
import { fetchMyProfile, updateMyProfile, UserProfile } from "../api/user";
import "../styles/Profile.css";

const ProfilePage: React.FC = () => {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);

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

    if (loading) return <div className="profile-page">Loading...</div>;
    if (error) return <div className="profile-page error">Error: {error}</div>;

    return (
        <div className="profile-page">
            <h2>Your Profile</h2>
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
        </div>
    );
};

export default ProfilePage;
