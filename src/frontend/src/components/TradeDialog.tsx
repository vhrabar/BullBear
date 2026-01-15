import {useMemo, useState} from "react";
import "../styles/TradeDialog.css";
import {getCSRFToken} from "../utils/csrf";

type OrderType = "MARKET" | "LIMIT" | "STOP" | "STOP_LIMIT";
type TimeInForce = "GTC" | "DAY" | "IOC" | "FOK";

interface TradeDialogProps {
    type: "buy" | "sell";
    symbol: string;
    price: number;

    onClose: () => void;
    onSuccess: () => void;
}

function TradeDialog({
                         type,
                         symbol,
                         price,
                         onClose,
                         onSuccess,
                     }: TradeDialogProps) {
    const [quantity, setQuantity] = useState<number>(1);

    const [orderType, setOrderType] = useState<OrderType>("MARKET");
    const [timeInForce, setTimeInForce] = useState<TimeInForce>("GTC");

    const [limitPrice, setLimitPrice] = useState<number>(price);
    const [stopPrice, setStopPrice] = useState<number>(price);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const side = type === "buy" ? "BUY" : "SELL";
    const endpoint = "/api/orders/orders/";

    const validate = (): string | null => {
        if (!Number.isFinite(quantity) || quantity <= 0) {
            return "Quantity must be greater than zero.";
        }

        if (orderType === "LIMIT" && (!limitPrice || limitPrice <= 0)) {
            return "Limit price must be greater than zero.";
        }

        if (orderType === "STOP" && (!stopPrice || stopPrice <= 0)) {
            return "Stop price must be greater than zero.";
        }

        if (orderType === "STOP_LIMIT") {
            if (!stopPrice || stopPrice <= 0) return "Stop price must be greater than zero.";
            if (!limitPrice || limitPrice <= 0) return "Limit price must be greater than zero.";
        }

        return null;
    };

    const submitOrder = async () => {
        const validationError = validate();
        if (validationError) {
            setError(validationError);
            return;
        }

        setLoading(true);
        setError(null);

        const csrftoken = getCSRFToken();

        const payload: Record<string, any> = {
            instrument_symbol: symbol,
            side,
            order_type: orderType,
            time_in_force: timeInForce,
            quantity,
        };

        if (orderType === "LIMIT" || orderType === "STOP_LIMIT") {
            payload.limit_price = limitPrice;
        }

        if (orderType === "STOP" || orderType === "STOP_LIMIT") {
            payload.stop_price = stopPrice;
        }
        console.log("ORDER PAYLOAD", payload);


        try {
            const res = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken!,
                },
                credentials: "include",
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                const contentType = res.headers.get("content-type") || "";
                let data: any = null;

                try {
                    if (contentType.includes("application/json")) {
                        data = await res.json();
                    } else {
                        data = await res.text();
                    }
                } catch {
                    // ignore fluff
                }

                console.log("ORDER ERROR STATUS:", res.status);
                console.log("ORDER ERROR BODY:", data);

                let message = `HTTP ${res.status}`;

                if (typeof data === "string") {
                    message = data.slice(0, 400);
                } else if (data?.detail) {
                    message = data.detail;
                } else if (data && typeof data === "object") {
                    message = Object.entries(data)
                        .map(([field, errors]) => {
                            if (Array.isArray(errors)) return `${field}: ${errors.join(" ")}`;
                            return `${field}: ${String(errors)}`;
                        })
                        .join(" | ");
                }

                throw new Error(message);
            }


            onSuccess();
            onClose();
        } catch (e: any) {
            setError(e?.message || "Order submission failed.");
        } finally {
            setLoading(false);
        }
    };

    const orderHelp = useMemo(() => {
        switch (orderType) {
            case "MARKET":
                return "Executes at the next available market price.";
            case "LIMIT":
                return side === "BUY"
                    ? "Executes only if price is at or below your limit."
                    : "Executes only if price is at or above your limit.";
            case "STOP":
                return side === "BUY"
                    ? "Triggers when price rises to your stop, then executes as market."
                    : "Triggers when price falls to your stop, then executes as market.";
            case "STOP_LIMIT":
                return "Triggers at stop price, then places a limit order.";
            default:
                return "";
        }
    }, [orderType, side]);

    return (
        <div className="trade-modal-backdrop">
            <div className="trade-modal">
                <h2 className="trade-title">
                    {type === "buy" ? "Buy" : "Sell"} {symbol}
                </h2>

                <p className="market-note">{orderHelp}</p>

                <div className="trade-field">
                    <label>Market Price:</label>
                    <input type="text" value={price.toFixed(2)} disabled/>
                </div>

                <div className="trade-field">
                    <label>Order Type:</label>
                    <select
                        value={orderType}
                        onChange={(e) => setOrderType(e.target.value as OrderType)}
                        disabled={loading}
                    >
                        <option value="MARKET">Market</option>
                        <option value="LIMIT">Limit</option>
                        <option value="STOP">Stop (Market)</option>
                        <option value="STOP_LIMIT">Stop-Limit</option>
                    </select>
                </div>

                <div className="trade-field">
                    <label>Time In Force:</label>
                    <select
                        value={timeInForce}
                        onChange={(e) => setTimeInForce(e.target.value as TimeInForce)}
                        disabled={loading}
                    >
                        <option value="GTC">GTC</option>
                        <option value="DAY">DAY</option>
                        <option value="IOC">IOC</option>
                        <option value="FOK">FOK</option>
                    </select>
                </div>

                {(orderType === "LIMIT" || orderType === "STOP_LIMIT") && (
                    <div className="trade-field">
                        <label>Limit Price:</label>
                        <input
                            type="number"
                            step="0.01"
                            value={limitPrice}
                            onChange={(e) => setLimitPrice(Number(e.target.value))}
                            disabled={loading}
                        />
                    </div>
                )}

                {(orderType === "STOP" || orderType === "STOP_LIMIT") && (
                    <div className="trade-field">
                        <label>Stop Price:</label>
                        <input
                            type="number"
                            step="0.01"
                            value={stopPrice}
                            onChange={(e) => setStopPrice(Number(e.target.value))}
                            disabled={loading}
                        />
                    </div>
                )}

                <div className="trade-field">
                    <label>Quantity:</label>
                    <input
                        type="number"
                        min={1}
                        value={quantity}
                        onChange={(e) => setQuantity(Number(e.target.value))}
                        disabled={loading}
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
                            ? "Submitting…"
                            : type === "buy"
                                ? "Place Buy Order"
                                : "Place Sell Order"}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default TradeDialog;
