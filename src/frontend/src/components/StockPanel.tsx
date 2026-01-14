import { useState } from "react";
import TradeDialog from "./TradeDialog.tsx";
import type { EarningsReport, Dividend } from "../types/stocks";


import "../styles/StockPanel.css";
import StockChart from "./StockChart.tsx";

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
  earnings?: EarningsReport[];
  dividends?: Dividend[];
}

interface NewsItem {
  id: number;
  headline: string;
   content?: string;
  published_at: string;
  url?: string;
}

interface StockPanelProps {
  stock: Instrument | null;
  holding?: Holding | null;
  latest?: LatestData | null;
  news?: NewsItem[];
}


function StockPanel({ stock, holding, latest, news, earnings, dividends }: StockPanelProps) {
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
                        <div className="chart-title">Price chart</div>
                        <StockChart instrument={stock.symbol} />
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
                        {news && news.length > 0 ? (
                          news.slice(0, 3).map((item) => (
                            <li key={item.id}>
                              {item.url ? (
                                <a href={item.url} target="_blank" rel="noopener noreferrer">
                                  {item.headline}
                                </a>
                              ) : (
                                <span>{item.headline}</span>
                              )}
                              <small>({new Date(item.published_at).toLocaleDateString()})</small>
                              {item.content && (
                                <p className="news-content">
                                  {item.content}
                                </p>
                              )}
                            </li>
                          ))
                        ) : (
                          <li>No news available</li>
                        )}
                      </ul>
                    </section>

                   <section className="panel-section">
                      <h3>Upcoming Earnings</h3>
                      <ul className="simple-list">
                        {earnings && earnings.length > 0 ? (
                          earnings.map((item) => (
                            <li key={item.id}>
                              {item.fiscal_quarter} {item.fiscal_year} –{" "}
                              {new Date(item.report_date).toLocaleDateString()} |
                              Estimate EPS: {item.estimate_eps ?? "—"}{" "}
                              {item.actual_eps !== null && (
                                <span style={{ color: "#34d399" }}>| Actual EPS: {item.actual_eps}</span>
                              )}
                            </li>
                          ))
                        ) : (
                          <li>No earnings scheduled</li>
                        )}
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
                  <h3>Upcoming Dividends</h3>
                  <ul className="simple-list">
                    {dividends && dividends.length > 0 ? (
                      dividends.map((item) => (
                        <li key={item.id}>
                          Ex-Date: {new Date(item.ex_date).toLocaleDateString()} | Amount:{" "}
                          {item.dividend_amount} {item.currency} | Payment Date:{" "}
                          {new Date(item.payment_date).toLocaleDateString()}
                        </li>
                      ))
                    ) : (
                      <li>No dividends scheduled</li>
                    )}
                  </ul>
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
