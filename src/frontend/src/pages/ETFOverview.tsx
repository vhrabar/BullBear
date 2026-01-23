import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import {PieChart} from "@mui/x-charts/PieChart";
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
}

interface HoldingDisplay {
    id: number;
    value: number;
    label: string;
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
                <h3>Holdings:</h3>
                {holdingsData.length === 0 ? (
                    <div className="empty">No holdings</div>
                ) : (
                    <>
                        <PieChart

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
