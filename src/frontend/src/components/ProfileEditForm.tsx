import "./profile-edit.css";
import { useState } from "react";

interface Props {
    user: any;
}

export default function ProfileEditForm({ user }: Props) {
    const [name, setName] = useState(user.name);
    const [bio, setBio] = useState(user.bio);
    const [saving, setSaving] = useState(false);

    async function onSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);

        // TODO: backend

        setSaving(false);
    }

    return (
        <form className="edit-form" onSubmit={onSubmit}>
            <div className="form-group">
                <label>Ime</label>
                <input
                    value={name}
                    onChange={e => setName(e.target.value)}
                    className="form-input"
                />
            </div>

            <div className="form-group">
                <label>Bio</label>
                <textarea
                    value={bio}
                    onChange={e => setBio(e.target.value)}
                    className="form-textarea"
                />
            </div>

            <button className="form-btn" disabled={saving}>
                {saving ? "Spremam..." : "Spremi"}
            </button>
        </form>
    );
}