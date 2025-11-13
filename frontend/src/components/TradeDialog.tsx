import { useState } from "react";
import "./TradeDialog.css";
import {getCSRFToken} from "../utils/csrf.ts";

interface TradeDIalogProps {
    type: "buy" | "sell";
    symbol: string;
    price: number;
    onClose: () => void;
    onSuccess: () => void;
}



function TradeDialog({ type, symbol, price, onClose, onSuccess }: TradeDIalogProps) {
    const [quantity, setQuantity] = useState<number>(1);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const endpoint = type === "buy" ? "/api/trading/buy" : "/api/trading/sell";

    const submitOrder = () => {
        if (quantity <= 0) {
            setError("Quantity must be greater than zero");
            return;
        }

        setLoading(true);
        setError(null);

        const csrftoken = getCSRFToken();
        fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken!,},
            credentials: "include",
            body: JSON.stringify({
                instrument_symbol: symbol,
                quantity,
                price,
            }),
        })
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                onSuccess();
                onClose();
            })
            .catch(() => {
                setError("Transaction failed.");
            })
            .finally(() => setLoading(false));
    };

    return (
        <div className="trade-modal-backdrop">
            <div className="trade-modal">

                <h2 className="trade-title">
                    {type === "buy" ? "Buy" : "Sell"} {symbol}
                </h2>

                <p className="market-note">
                    This system currently supports only market-price transactions.
                </p>

                <div className="trade-field">
                    <label>Market Price:</label>
                    <input type="text" value={price.toFixed(2)} disabled />
                </div>

                <div className="trade-field">
                    <label>Quantity:</label>
                    <input
                        type="number"
                        min={1}
                        value={quantity}
                        onChange={(e) => setQuantity(Number(e.target.value))}
                    />
                </div>

                {error && <div className="trade-error">{error}</div>}

                <div className="trade-actions">
                    <button className="btn cancel" onClick={onClose} disabled={loading}>
                        Cancel
                    </button>

                    <button
                        className={type === "buy" ? "btn buy" : "btn sell"}
                        onClick={submitOrder}
                        disabled={loading}
                    >
                        {loading
                            ? "Processing…"
                            : type === "buy"
                            ? "Confirm Buy"
                            : "Confirm Sell"}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default TradeDialog;
