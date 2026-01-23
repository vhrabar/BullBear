import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import {PieChart} from "@mui/x-charts/PieChart";
import {LineChart} from "@mui/x-charts/LineChart";
import { getCSRFToken } from "../utils/csrf";
import './ETFManage.css';

interface ETF {
    id: number;
    creator_portfolio: number;
    name: string;
    description: string;
    is_active: boolean;
    total_units: number;
    nav_per_unit: number;
    holdings: any[];
    owner_username: string;
    subscriber_count: number;
    total_invested: number;
    created_at: string;
    updated_at: string;
}

interface HoldingDisplay {
    id: number;
    value: number;
    label: string;
}

interface PerformanceData {
    nav_per_unit: number;
    recorded_at: string;
}

function ETFView() {
    const params = useParams();
    const [loading, setLoading] = useState(true);
    const [state, setState] = useState(0); // 0: undefined, 1: owner, 2: subscribed, 3: unsubscribed
    const [etf, setEtf] = useState<ETF | null>(null);
    const [val, setVal] = useState(0);
    const [portfolioId, setPortfolioId] = useState<number | null>(null);
    const [subscriptionId, setSubscriptionId] = useState<number | null>(null);
    const [holdingsData, setHoldingsData] = useState<HoldingDisplay[]>([]);
    const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // Fetch portfolio details
                const portfolioRes = await fetch("/api/users/portofolio-details/", {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include"
                });
                if (!portfolioRes.ok) throw new Error(`HTTP ${portfolioRes.status}`);
                const portfolioData = await portfolioRes.json();
                const portfolioIdValue = Array.isArray(portfolioData) ? portfolioData[0].id : portfolioData.id;
                setPortfolioId(portfolioIdValue);

                // Fetch fund details
                const fundRes = await fetch("/api/funds/funds/" + params.id + "/", {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                });
                if (!fundRes.ok) throw new Error(`HTTP ${fundRes.status}`);
                const fundData: ETF = await fundRes.json();
                setEtf(fundData);

                // Fetch all instruments to get names
                const instrumentsRes = await fetch("/api/trading/instruments/", {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                });
                if (!instrumentsRes.ok) throw new Error(`HTTP ${instrumentsRes.status}`);
                const allInstruments = await instrumentsRes.json();

                // Map holdings with instrument names
                const holdingsWithNames = fundData.holdings.map((x, index) => {
                    const instrument = allInstruments.find((inst: any) => inst.id === x.instrument);
                    return {
                        id: index,
                        value: parseFloat(x.weight_percent),
                        label: instrument ? instrument.name : `Instrument ${x.instrument}`
                    };
                });
                setHoldingsData(holdingsWithNames);

                // Fetch performance data
                try {
                    const perfRes = await fetch("/api/funds/funds/" + params.id + "/performance/?days=30", {
                        method: "GET",
                        headers: { "Content-Type": "application/json" },
                        credentials: "include",
                    });
                    if (perfRes.ok) {
                        const perfData = await perfRes.json();
                        setPerformanceData(perfData);
                    }
                } catch (err) {
                    console.error("Failed to load performance data:", err);
                }

                // Determine state
                if (fundData.creator_portfolio === portfolioIdValue) {
                    setState(1);
                } else {
                    // Check for subscription
                    try {
                        const subRes = await fetch("/api/funds/subscriptions/", {
                            method: "GET",
                            headers: { "Content-Type": "application/json" },
                            credentials: "include",
                        });
                        if (subRes.ok) {
                            const subscriptions = await subRes.json();
                            const userSub = subscriptions.find(
                                (s: any) => s.fund === fundData.id && s.subscriber_portfolio === portfolioIdValue
                            );
                            if (userSub) {
                                setVal(userSub.units || userSub.invested_amount / fundData.nav_per_unit);
                                setSubscriptionId(userSub.id);
                                setState(2);
                            } else {
                                setState(3);
                            }
                        } else {
                            setState(3);
                        }
                    } catch {
                        setState(3);
                    }
                }
            } catch (error) {
                console.error("Failed to load ETF data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [params.id]);

    async function del() {
        const csrftoken = getCSRFToken();
        await fetch("/api/funds/funds/" + params.id + "/", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken || "",
            },
            credentials: "include",
        })
        .then(async (res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            window.location.href = "/ETF/explore";
        });
    }

    async function unSub() {
        if (!subscriptionId) return;
        const csrftoken = getCSRFToken();
        await fetch("/api/funds/subscriptions/" + subscriptionId + "/", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken || "",
            },
            credentials: "include",
        })
        .then(async (res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            window.location.reload();
        });
    }

    async function sub() {
        const amount = Math.max(Math.round(val), 0);
        if (amount === 0) return;
        const csrftoken = getCSRFToken();
        await fetch("/api/funds/subscriptions/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken || "",
            },
            credentials: "include",
            body: JSON.stringify({
                subscriber_portfolio: portfolioId,
                fund: Number(params.id),
                invested_amount: amount * ((etf === null) ? 0 : etf.nav_per_unit)
            })
        })
        .then(async (res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            window.location.reload();
        });
    }

    async function reSub() {
        const amount = Math.max(Math.round(val), 0);
        if (amount === 0 || !subscriptionId) return;
        const csrftoken = getCSRFToken();
        await fetch("/api/funds/subscriptions/" + subscriptionId + "/", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken || "",
            },
            credentials: "include",
            body: JSON.stringify({
                subscriber_portfolio: portfolioId,
                fund: Number(params.id),
                invested_amount: amount * ((etf === null) ? 0 : etf.nav_per_unit)
            })
        })
        .then(async (res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            window.location.reload();
        });
    }

    if (loading) {
        return <div className="etf-container"><div className="loading">Loading...</div></div>;
    }

    if (etf === null) {
        return <div className="etf-container"><div className="error">ETF not found</div></div>;
    }

    return (
        <div className="etf-container">
            <div className="etf-overview">
                <h2>{etf.name}</h2>
                <p>{etf.description}</p>

                {/* Fund Info Section */}
                <div className="fund-info">
                    <h3>Fund Information</h3>
                    <table className="info-table">
                        <tbody>
                            <tr>
                                <td><strong>Owner:</strong></td>
                                <td>{etf.owner_username || 'Unknown'}</td>
                            </tr>
                            <tr>
                                <td><strong>NAV per Unit:</strong></td>
                                <td>${Number(etf.nav_per_unit).toFixed(2)}</td>
                            </tr>
                            <tr>
                                <td><strong>Total Units:</strong></td>
                                <td>{Number(etf.total_units).toFixed(2)}</td>
                            </tr>
                            <tr>
                                <td><strong>Subscribers:</strong></td>
                                <td>{etf.subscriber_count || 0}</td>
                            </tr>
                            <tr>
                                <td><strong>Total Invested:</strong></td>
                                <td>${Number(etf.total_invested || 0).toFixed(2)}</td>
                            </tr>
                            <tr>
                                <td><strong>Created:</strong></td>
                                <td>{etf.created_at ? new Date(etf.created_at).toLocaleDateString() : 'N/A'}</td>
                            </tr>
                            <tr>
                                <td><strong>Last Updated:</strong></td>
                                <td>{etf.updated_at ? new Date(etf.updated_at).toLocaleDateString() : 'N/A'}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                {/* Performance Chart Section */}
                {performanceData.length > 0 && (
                    <div className="performance-section">
                        <h3>Performance (Last 30 Days)</h3>
                        <LineChart
                            xAxis={[{
                                data: performanceData.map((_, i) => i),
                                scaleType: 'point',
                                valueFormatter: (value) => {
                                    const item = performanceData[value];
                                    return item ? new Date(item.recorded_at).toLocaleDateString() : '';
                                }
                            }]}
                            series={[{
                                data: performanceData.map(p => Number(p.nav_per_unit)),
                                label: 'NAV per Unit',
                                color: '#4caf50'
                            }]}
                            width={500}
                            height={300}
                        />
                    </div>
                )}

                <h3>Holdings:</h3>
                {holdingsData.length === 0 ? (
                    <div className="empty">No holdings</div>
                ) : (
                    <>
                        <PieChart
                            series={[{
                                data: holdingsData,
                                innerRadius: 30,
                                outerRadius: 100,
                                paddingAngle: 2,
                                cornerRadius: 5
                            }]}
                            width={400}
                            height={250}
                        />
                        <table className="holdings-table">
                            <thead>
                                <tr>
                                    <th>Instrument</th>
                                    <th>Weight</th>
                                </tr>
                            </thead>
                            <tbody>
                                {holdingsData.map((h) => (
                                    <tr key={h.id}>
                                        <td>{h.label}</td>
                                        <td>{h.value.toFixed(2)}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </>
                )}
                <div className="etf-actions">
                    {state === 1 ? (
                        <>
                            <a href={"/ETF/edit/" + params.id}><button>Edit ETF</button></a>
                            <button className="delete-btn" onClick={del}>Delete</button>
                        </>
                    ) : state === 2 ? (
                        <>
                            <label htmlFor="amount">Broj udjela: </label>
                            <input
                                id="amount"
                                name="amount"
                                type="number"
                                min={0}
                                value={val}
                                step={1}
                                onChange={(e) => setVal(Number(e.target.value))}
                            />
                            <button onClick={reSub}>Change investment</button>
                            <button className="delete-btn" onClick={unSub}>Unsubscribe</button>
                        </>
                    ) : state === 3 ? (
                        <>
                            <label htmlFor="amount">Broj udjela: </label>
                            <input
                                id="amount"
                                name="amount"
                                type="number"
                                min={0}
                                value={val}
                                step={1}
                                onChange={(e) => setVal(Number(e.target.value))}
                            />
                            <button onClick={sub}>Invest</button>
                        </>
                    ) : null}
                </div>
            </div>
        </div>
    );
}

export default ETFView;
