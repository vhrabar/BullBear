import { useState, useEffect, ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import { toggleFavorite } from "../api/favorites";
import "../styles/ExplorePage.css";

interface InstrumentItem {
    id: number;
    symbol: string;
    name: string;
    type: string;
    exchange: string;
    currency: string;
    is_active: boolean;
}

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

interface InstrumentExtended extends InstrumentItem {
    latestCandle?: CandleData | null;
    ask?: number | null;
    isFavorite?: boolean;
}

function ExchangePage() {
    const [instruments, setInstruments] = useState<InstrumentExtended[]>([]);
    const [filtered, setFiltered] = useState<InstrumentExtended[]>([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [, setFavoriteIds] = useState<Set<number>>(new Set());

    const navigate = useNavigate();

    // Load instruments and favorites
    useEffect(() => {
        Promise.all([
            fetch("/api/trading/instruments/", {
                method: "GET",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
            }).then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            }),
            fetch("/api/trading/favorites/", {
                method: "GET",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
            }).then(res => res.ok ? res.json() : [])
        ])
            .then(([instrumentsData, favoritesData]) => {
                const favIds = new Set<number>(favoritesData.map((f: any) => f.instrument));
                setFavoriteIds(favIds);

                const instrumentsWithFav = instrumentsData.map((item: InstrumentItem) => ({
                    ...item,
                    isFavorite: favIds.has(item.id)
                }));
                setInstruments(instrumentsWithFav);
                setFiltered(instrumentsWithFav);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    // Fetch latest data
    useEffect(() => {
        if (filtered.length === 0) return;

        async function fetchLatest() {
            const updated = await Promise.all(
                filtered.map(async (item) => {
                    try {
                        const res = await fetch(
                            `/api/trading/latest-instrument-data/?instrument=${item.symbol}`,
                            { credentials: "include" }
                        );
                        if (!res.ok) return { ...item, latestCandle: null };

                        const data = await res.json();
                        const candle = Array.isArray(data) && data.length > 0 ? data[0] : null;

                        return {
                            ...item,
                            latestCandle: candle,
                            ask: candle ? Number(candle.close_price) : null,
                        };
                    } catch {
                        return { ...item, latestCandle: null };
                    }
                })
            );

            setFiltered(updated);
        }

        fetchLatest();
    }, [filtered.length]);

    const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
        const q = e.target.value.toLowerCase();
        setSearch(q);

        const results = instruments.filter((item) =>
            item.symbol.toLowerCase().includes(q) ||
            item.name.toLowerCase().includes(q) ||
            item.exchange.toLowerCase().includes(q) ||
            item.currency.toLowerCase().includes(q)
        );

        setFiltered(results);
    };

    const handleToggleFavorite = async (instrumentId: number, e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            const result = await toggleFavorite(instrumentId);

            // Update favorite status in both lists
            const updateFavoriteStatus = (items: InstrumentExtended[]) =>
                items.map(item =>
                    item.id === instrumentId
                        ? { ...item, isFavorite: result.is_favorite }
                        : item
                );

            setInstruments(updateFavoriteStatus);
            setFiltered(updateFavoriteStatus);

            // Update favoriteIds set
            setFavoriteIds(prev => {
                const newSet = new Set(prev);
                if (result.is_favorite) {
                    newSet.add(instrumentId);
                } else {
                    newSet.delete(instrumentId);
                }
                return newSet;
            });
        } catch (err) {
            console.error("Failed to toggle favorite:", err);
        }
    };

    if (loading) return <div id="loading">Loading…</div>;
    if (error) return <div id="error">Error: {error}</div>;

    return (
        <div id="container-root">

            <div className="search-bar">
                <input
                    type="text"
                    value={search}
                    onChange={handleSearch}
                    placeholder="Search instruments..."
                />
            </div>

            {filtered.length === 0 ? (
                <div id="empty">No instruments match your search.</div>
            ) : (
                <table id="container">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Name</th>
                            <th>Ask</th>
                            <th>Last</th>
                            <th>Exchange</th>
                            <th>Currency</th>
                            <th>Favorite</th>
                        </tr>
                    </thead>

                    <tbody>
                        {filtered.map((x) => (
                            <tr
                                key={x.id}
                                className="stock-item"
                                onClick={() => navigate(`/quote/${x.symbol}`)}
                            >
                                <td>{x.symbol}</td>
                                <td>{x.name}</td>
                                <td>{x.ask ?? "—"}</td>
                                <td>{x.latestCandle?.close_price ?? "—"}</td>
                                <td>{x.exchange}</td>
                                <td>{x.currency}</td>
                                <td>
                                    <button
                                        className={`fav-btn ${x.isFavorite ? "is-favorite" : ""}`}
                                        onClick={(e) => handleToggleFavorite(x.id, e)}
                                        title={x.isFavorite ? "Remove from favorites" : "Add to favorites"}
                                    >
                                        {x.isFavorite ? "★" : "☆"}
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

export default ExchangePage;
