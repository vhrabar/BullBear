import {Holding} from "./StockView";
import "./StockPanel.css";

interface StockPanelProps {
    selected: Holding | null,
    latest?: LatestData | null
}


interface LatestData {
    ask_price: number;
    bid_price: number;
    ask_size: number;
    bid_size: number;
}

function StockPanel({selected, latest}: StockPanelProps) {
    if (!selected) {
        return (
            <div className="stock-panel empty">
                <div className="empty-message">
                    No stock selected. Please select a stock from your portfolio.
                </div>
            </div>
        );
    }

    const [tickerPart, companyPartRaw] = selected.instrument.split("(");
    const companyPart = companyPartRaw ? companyPartRaw.split(")")[0] : "";

    return (
        <div className="stock-panel">
            <div className="stock-panel-header">
                <div>
                    <div className="stock-name">
                        {tickerPart.trim()} <span className="company-name">{companyPart}</span>
                    </div>
                    <div className="stock-sub">
                        Current value: {selected.current_value} | Quantity: {selected.quantity}
                    </div>
                </div>
                {latest && (
                    <div className="stock-sub">
                        <div>
                            Buy: {latest.ask_price} | Sell: {latest.bid_price}
                        </div>
                        <div>
                            Size: {latest.ask_size} | {latest.bid_size}
                        </div>
                    </div>
                )}
                <div className="stock-actions">
                    <button className="btn buy">Buy</button>
                    <button className="btn sell">Sell</button>
                </div>
            </div>

            <div className="stock-panel-main">
                <div className="stock-main-left">
                    <div className="chart-placeholder">
                        <div className="chart-title">Price chart (placeholder)</div>
                        <div className="chart-body">
                        </div>
                    </div>

                    <div className="metrics-card">
                        <div className="metric-row">
                            <span>Shares</span>
                            <span>{selected.quantity}</span>
                        </div>
                        <div className="metric-row">
                            <span>Market Value</span>
                            <span>{selected.current_value}</span>
                        </div>
                        <div className="metric-row">
                            <span>Average Price</span>
                            <span>{selected.average_price}</span>
                        </div>
                        <div className="metric-row">
                            <span>Profit / Loss</span>
                            <span
                                style={
                                    selected.profit_loss[0] === "-"
                                        ? {color: "red"}
                                        : {color: "green"}
                                }
                            >
                {selected.profit_loss}
              </span>
                        </div>
                    </div>
                </div>

                <div className="stock-main-right">
                    <section className="panel-section">
                        <h3>Hot News</h3>
                        <ul className="simple-list">
                            <li>News 1 about {tickerPart.trim()} (placeholder)</li>
                            <li>News 2 about {tickerPart.trim()} (placeholder)</li>
                            <li>News 3 about {tickerPart.trim()} (placeholder)</li>
                        </ul>
                    </section>

                    <section className="panel-section">
                        <h3>Upcoming Events</h3>
                        <ul className="simple-list">
                            <li>Earnings – placeholder date</li>
                            <li>Options expiry – placeholder</li>
                        </ul>
                    </section>
                </div>
            </div>

            <div className="stock-panel-bottom">
                <section className="panel-section">
                    <h3>Transaction History</h3>
                    <div className="history-placeholder">
                        No history implemented yet.
                    </div>
                </section>

                <section className="panel-section">
                    <h3>Dividends</h3>
                    <div className="history-placeholder">
                        Dividend data placeholder.
                    </div>
                </section>
            </div>
        </div>
    );
}

export default StockPanel;
