import { useState } from "react";
import TradeDialog from "./TradeDialog.tsx";


import "./StockPanel.css";

interface Instrument {
  symbol: string;
  name: string;
}

interface Holding {
  quantity: string;
  current_value: string;
  average_price: string;
  profit_loss: string;
  instrument: string;
}

interface LatestData {
  bid_price?: string;
  bid_size?: number;
  ask_price?: string;
  ask_size?: number;
  last_price?: string;
  daily_change?: string;
  daily_change_percent?: string;

  open_price?: string;
  high_price?: string;
  low_price?: string;
  close_price?: string;
}

interface StockPanelProps {
  stock: Instrument | null;
  holding?: Holding | null;
  latest?: LatestData | null;
}


function StockPanel({ stock, holding, latest }: StockPanelProps) {
    if (!stock) {
        return (
            <div className="stock-panel empty">
                <div className="empty-message">
                    No stock selected.
                </div>
            </div>
        );
    }

    const ticker = stock.symbol;
    const company = stock.name;
    const [tradeType, setTradeType] = useState<"buy" | "sell" | null>(null);



    return (
        <div className="stock-panel">
            <div className="stock-panel-header">

                <div>
                    <div className="stock-name">
                        {ticker} <span className="company-name">{company}</span>
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
                </div>

               <div className="stock-actions">
                <button className="btn buy" onClick={() => setTradeType("buy")}>Buy</button>
                <button className="btn sell" onClick={() => setTradeType("sell")}>Sell</button>
            </div>

            </div>

            <div className="stock-panel-main">
                <div className="stock-main-left">

                    <div className="chart-placeholder">
                        <div className="chart-title">Price chart (placeholder)</div>
                        <div className="chart-body"></div>
                    </div>

                    <div className="metrics-card">

                        <div className="metric-row">
                            <span>Open</span>
                            <span>{latest?.open_price ?? "—"}</span>
                        </div>

                        <div className="metric-row">
                            <span>Close</span>
                            <span>{latest?.close_price ?? "—"}</span>
                        </div>

                        <div className="metric-row">
                            <span>High</span>
                            <span>{latest?.high_price ?? "—"}</span>
                        </div>

                        <div className="metric-row">
                            <span>Low</span>
                            <span>{latest?.low_price ?? "—"}</span>
                        </div>

                        {holding && (
                            <>
                                <div className="metric-row">
                                    <span>Shares Owned</span>
                                    <span>{holding.quantity}</span>
                                </div>

                                <div className="metric-row">
                                    <span>Average Price</span>
                                    <span>{holding.average_price}</span>
                                </div>

                                <div className="metric-row">
                                    <span>Market Value</span>
                                    <span>{holding.current_value}</span>
                                </div>

                                <div className="metric-row">
                                    <span>Profit/Loss</span>
                                    <span
                                        style={
                                            holding.profit_loss.startsWith("-")
                                                ? { color: "red" }
                                                : { color: "green" }
                                        }
                                    >
                                        {holding.profit_loss}
                                    </span>
                                </div>
                            </>
                        )}

                    </div>
                </div>

                <div className="stock-main-right">
                    <section className="panel-section">
                        <h3>Hot News</h3>
                        <ul className="simple-list">
                            <li>News 1 about {ticker} (placeholder)</li>
                            <li>News 2 about {ticker} (placeholder)</li>
                            <li>News 3 about {ticker} (placeholder)</li>
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

            {tradeType && latest && (
            <TradeDialog
                type={tradeType}
                symbol={ticker}
                price={Number(latest.last_price || latest.ask_price || latest.close_price)}
                onClose={() => setTradeType(null)}
                onSuccess={() => {
                    console.log("Trade completed successfully.");
                }}
            />
        )}

        </div>



    );
}

export default StockPanel;
