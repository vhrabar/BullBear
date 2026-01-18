import {useEffect, useMemo, useState} from "react";
import StockView from "../components/StockView.tsx";
import PortfolioPerformancePanel from "../components/PortfolioPerfomace.tsx";
import "../styles/PortfolioPage.css";

type PortfolioDetails = {
    id: number;
    name?: string;
    balance: string | number;
};

function PortfolioPage() {
    const [portfolio, setPortfolio] = useState<PortfolioDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchPortfolio() {
            setLoading(true);
            setError(null);

            try {
                const response = await fetch("/api/users/portofolio-details", {
                    method: "GET",
                    headers: {"Content-Type": "application/json"},
                    credentials: "include",
                });

                if (!response.ok) throw new Error("Unable to fetch portfolio information.");

                const data = await response.json();
                if (Array.isArray(data) && data.length > 0) {
                    const p = data[0];
                    setPortfolio({
                        id: Number(p.id ?? p.portfolio_id ?? p.pk ?? 0),
                        name: p.name ?? "Main Portfolio",
                        balance: p.balance ?? "0",
                    });
                } else {
                    setPortfolio(null);
                }
            } catch (err: any) {
                setError(err?.message ?? "Unknown error");
            } finally {
                setLoading(false);
            }
        }

        fetchPortfolio();
    }, []);

    const balanceText = useMemo(() => {
        if (!portfolio) return "—";
        const n = typeof portfolio.balance === "number" ? portfolio.balance : Number(portfolio.balance);
        return Number.isFinite(n) ? n.toFixed(2) : String(portfolio.balance);
    }, [portfolio]);

    return (
        <div className="portfolio-page">
            <div className="portfolio-container">
                {/* Header */}
                <div className="portfolio-header">
                    <div>
                        <div className="portfolio-title-main">Portfolio</div>
                        <div className="portfolio-title-sub">Holdings, performance and risk</div>
                    </div>
                    <div className="portfolio-badge">
                        {loading ? "Loading..." : error ? "Error" : "Active"}
                    </div>
                </div>

                {/* Top metrics strip */}
                <div className="portfolio-metrics">
                    <div className="metric">
                        <div className="metric-label">Name</div>
                        <div className="metric-value">{portfolio?.name ?? "—"}</div>
                    </div>
                    <div className="metric">
                        <div className="metric-label">Cash balance</div>
                        <div className="metric-value">{loading ? "..." : balanceText}</div>
                    </div>
                    <div className="metric">
                        <div className="metric-label">Snapshots</div>
                        <div className="metric-value blue">10m</div>
                    </div>
                </div>

                {error && (
                    <div className="portfolio-alert">
                        <div className="portfolio-alert-title">Error</div>
                        <div className="portfolio-alert-body">{error}</div>
                    </div>
                )}

                {/* MAIN DASHBOARD GRID */}
                <div className="portfolio-dashboard">
                    {/* LEFT: Holdings */}
                    <div className="panel panel-holdings">
                        <div className="panel-header">
                            <div className="panel-title">Holdings</div>
                            <div className="panel-subtitle">Your open positions and P/L</div>
                        </div>
                        <div className="holdings-body">
                            <StockView/>
                        </div>
                    </div>

                    {/* RIGHT: Performance + Risk stacked */}
                    <div className="portfolio-right">
                        <div className="panel panel-performance">
                            {portfolio?.id ? (
                                <PortfolioPerformancePanel
                                    portfolioId={portfolio.id}
                                    title="Performance"
                                    subtitle="Total value, allocation, unrealized P/L"
                                />
                            ) : (
                                <div className="panel-empty">No portfolio id found.</div>
                            )}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}

export default PortfolioPage;
