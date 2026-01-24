import { getCSRFToken } from "../utils/csrf";

export interface Instrument {
  id: number;
  symbol: string;
  name: string;
  type: string;
  exchange: string;
  currency: string;
  is_active: boolean;
}

export interface FavoriteInstrument {
  id: number;
  instrument: number;
  instrument_details: Instrument;
  added_at: string;
}

export interface ToggleResponse {
  is_favorite: boolean;
  message: string;
}

const API_BASE = "/api/trading/favorites";

/**
 * Fetch all favorite instruments for the current user.
 */
export async function getFavorites(): Promise<FavoriteInstrument[]> {
  const res = await fetch(`${API_BASE}/`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch favorites: ${res.status}`);
  }

  return res.json();
}

/**
 * Add an instrument to favorites.
 */
export async function addFavorite(instrumentId: number): Promise<FavoriteInstrument> {
  const csrfToken = getCSRFToken();
  const res = await fetch(`${API_BASE}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(csrfToken && { "X-CSRFToken": csrfToken }),
    },
    credentials: "include",
    body: JSON.stringify({ instrument_id: instrumentId }),
  });

  if (!res.ok) {
    throw new Error(`Failed to add favorite: ${res.status}`);
  }

  return res.json();
}

/**
 * Remove an instrument from favorites.
 */
export async function removeFavorite(favoriteId: number): Promise<void> {
  const csrfToken = getCSRFToken();
  const res = await fetch(`${API_BASE}/${favoriteId}/`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      ...(csrfToken && { "X-CSRFToken": csrfToken }),
    },
    credentials: "include",
  });

  if (!res.ok) {
    throw new Error(`Failed to remove favorite: ${res.status}`);
  }
}

/**
 * Toggle favorite status for an instrument.
 */
export async function toggleFavorite(instrumentId: number): Promise<ToggleResponse> {
  const csrfToken = getCSRFToken();
  const res = await fetch(`${API_BASE}/toggle/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(csrfToken && { "X-CSRFToken": csrfToken }),
    },
    credentials: "include",
    body: JSON.stringify({ instrument_id: instrumentId }),
  });

  if (!res.ok) {
    throw new Error(`Failed to toggle favorite: ${res.status}`);
  }

  return res.json();
}

/**
 * Check if an instrument is in user's favorites.
 */
export async function checkFavorite(instrumentId: number): Promise<boolean> {
  const res = await fetch(`${API_BASE}/check/?instrument_id=${instrumentId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  });

  if (!res.ok) {
    throw new Error(`Failed to check favorite: ${res.status}`);
  }

  const data = await res.json();
  return data.is_favorite;
}

