export type UserProfile = {
    id: number;
    user: number;
    bio: string;
    avatar_url?: string;
    username?: string;
    first_name?: string;
    last_name?: string;
    subscription?: {
        package_id: number;
        package_price: string;
        subscription_type: {
            id: number;
            name: string;
            price: string;
            duration_days: number;
        };
        start_date: string;
        end_date: string;
        is_active: boolean;
    } | null;
};

export type UserUpdatePayload = {
    bio?: string;
    avatar_url?: string;
    username?: string;
    first_name?: string;
    last_name?: string;
};

import { getCSRFToken } from "../utils/csrf";

export async function fetchMyProfile(): Promise<UserProfile> {
    const r = await fetch("/api/users/user-profile/me/", {
        method: "GET",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
}

export async function updateMyProfile(payload: UserUpdatePayload) {
    const token = getCSRFToken();
    const r = await fetch("/api/users/user-profile/me/", {
        method: "PATCH",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            ...(token ? { "X-CSRFToken": token } : {}),
        },
        body: JSON.stringify(payload),
    });
    if (!r.ok) {
        const text = await r.text();
        throw new Error(text || `HTTP ${r.status}`);
    }
    return r.json();
}
