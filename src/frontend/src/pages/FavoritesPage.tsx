import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getFavorites, removeFavorite, FavoriteInstrument } from "../api/favorites";
import "../styles/FavoritesPage.css";

interface CandleData {
  id: number;
  instrument: string;
  start_time: string;
  end_time: string;
  open_price: string;
  high_price: string;
  low_price: string;
  close_price: string;
  volume: number | null;
  updated_at: string;
}

interface FavoriteExtended extends FavoriteInstrument {
  latestCandle?: CandleData | null;
  currentPrice?: number | null;
}

function FavoritesPage() {
  const [favorites, setFavorites] = useState<FavoriteExtended[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  // Load favorites
  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      setLoading(true);
      const data = await getFavorites();
      setFavorites(data);
      setLoading(false);

      // After loading favorites, fetch latest prices
      if (data.length > 0) {
        fetchLatestPrices(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load favorites");
      setLoading(false);
    }
  };

  const fetchLatestPrices = async (favs: FavoriteInstrument[]) => {
    const updated = await Promise.all(
      favs.map(async (fav) => {
        try {
          const res = await fetch(
            `/api/trading/latest-instrument-data/?instrument=${fav.instrument_details.symbol}`,
            { credentials: "include" }
          );
          if (!res.ok) return { ...fav, latestCandle: null, currentPrice: null };

          const data = await res.json();
          const candle = Array.isArray(data) && data.length > 0 ? data[0] : null;

          return {
            ...fav,
            latestCandle: candle,
            currentPrice: candle ? Number(candle.close_price) : null,
          };
        } catch {
          return { ...fav, latestCandle: null, currentPrice: null };
        }
      })
    );

    setFavorites(updated);
  };

  const handleRemoveFavorite = async (favoriteId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await removeFavorite(favoriteId);
      setFavorites((prev) => prev.filter((f) => f.id !== favoriteId));
    } catch (err) {
      console.error("Failed to remove favorite:", err);
    }
  };

  if (loading) return <div className="favorites-loading">Loading favorites…</div>;
  if (error) return <div className="favorites-error">Error: {error}</div>;

  return (
    <div className="favorites-container">
      <div className="favorites-header">
        <h1>Favorite Instruments</h1>
        <p className="favorites-subtitle">
          Your watchlist of instruments you're following
        </p>
      </div>

      {favorites.length === 0 ? (
        <div className="favorites-empty">
          <h2>No favorites yet</h2>
          <p>
            Start adding instruments to your favorites from the{" "}
            <span className="link" onClick={() => navigate("/explore")}>
              Explore
            </span>{" "}
            page.
          </p>
        </div>
      ) : (
        <table className="favorites-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th>Type</th>
              <th>Price</th>
              <th>Exchange</th>
              <th>Added</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {favorites.map((fav) => (
              <tr
                key={fav.id}
                className="favorite-row"
                onClick={() => navigate(`/quote/${fav.instrument_details.symbol}`)}
              >
                <td className="symbol-cell">{fav.instrument_details.symbol}</td>
                <td className="name-cell">{fav.instrument_details.name}</td>
                <td>{fav.instrument_details.type}</td>
                <td className="price-cell">
                  {fav.currentPrice ? `$${fav.currentPrice.toFixed(2)}` : "—"}
                </td>
                <td>{fav.instrument_details.exchange || "—"}</td>
                <td className="date-cell">
                  {new Date(fav.added_at).toLocaleDateString()}
                </td>
                <td>
                  <button
                    className="remove-btn"
                    onClick={(e) => handleRemoveFavorite(fav.id, e)}
                    title="Remove from favorites"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default FavoritesPage;
