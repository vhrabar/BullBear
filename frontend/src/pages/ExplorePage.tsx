import { useState, useEffect, ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import "./ExplorePage.css";

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
}

function ExchangePage() {
    const [instruments, setInstruments] = useState<InstrumentExtended[]>([]);
    const [filtered, setFiltered] = useState<InstrumentExtended[]>([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const navigate = useNavigate();

    // Load instruments
    useEffect(() => {
        fetch("/api/trading/instruments/", {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
        })
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then((data) => {
                setInstruments(data);
                setFiltered(data);
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
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default ExchangePage;
