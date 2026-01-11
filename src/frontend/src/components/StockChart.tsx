import React, {useEffect, useMemo, useRef, useState} from "react";
import axios from "axios";
import {
    ChartCanvas,
    Chart,
    CandlestickSeries,
    BarSeries,
    LineSeries,
    XAxis,
    YAxis,
    MouseCoordinateX,
    MouseCoordinateY,
    CrossHairCursor,
    SingleValueTooltip,
    ema,
    discontinuousTimeScaleProviderBuilder,
} from "react-financial-charts";
import {timeFormat} from "d3-time-format";
import {format} from "d3-format";

interface StockData {
    date: Date;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    ema20?: number;
}

interface StockChartProps {
    instrument: string;
}

type TimeRange = "24H" | "1W" | "1M" | "3M" | "ALL";

const axisStyle = {
    stroke: "#475569",
    tickStroke: "#475569",
    tickLabelFill: "#e5e7eb",
};

// ime format helpers
const fmtTime = timeFormat("%H:%M");
const fmtDayTime = timeFormat("%b %d %H:%M");
const fmtDay = timeFormat("%b %d");
const fmDayMonth = timeFormat("%b %d %Y");
const fmtMonth = timeFormat("%b %Y");
// const fmtYear = timeFormat("%Y"); -> not enough data points TODO: import yearly data from Massive CSV

function getTickFormat(range: TimeRange) {
    switch (range) {
        case "24H":
            return fmtTime;
        case "1W":
            return fmtDayTime;
        case "1M":
            return fmtDay;
        case "3M":
            return fmDayMonth;
        case "ALL":
        default:
            return fmtMonth;
    }
}

export default function StockChart({instrument}: StockChartProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    const [dimensions, setDimensions] = useState({width: 0, height: 0});
    const [rawData, setRawData] = useState<StockData[]>([]);
    const [range, setRange] = useState<TimeRange>("ALL");

    // handle resize
    useEffect(() => {
        if (!containerRef.current) return;

        const observer = new ResizeObserver((entries) => {
            const {width, height} = entries[0].contentRect;
            setDimensions({width, height});
        });

        observer.observe(containerRef.current);
        return () => observer.disconnect();
    }, []);

    // fetch data
    useEffect(() => {
        const controller = new AbortController();

        async function fetchData() {
            try {
                const res = await axios.get(
                    `/api/trading/instrument-data/?instrument=${instrument}`,
                    {signal: controller.signal}
                );

                const parsed: StockData[] = res.data
                    .map((item: any) => {
                        const date = new Date(item.start_time);
                        if (isNaN(date.getTime())) return null;
                        console.log(date);
                        return {
                            date,
                            open: +item.open_price,
                            high: +item.high_price,
                            low: +item.low_price,
                            close: +item.close_price,
                            volume: Number(item.volume) || 0,
                        };
                    })
                    .filter((d: StockData | null): d is StockData => d !== null)
                    .sort(
                        (a: StockData, b: StockData) =>
                            a.date.getTime() - b.date.getTime()
                    );

                setRawData(parsed);
            } catch (err: any) {
                if (err.code === "ERR_CANCELED") return;
                throw err;
            }
        }

        fetchData();
        return () => controller.abort();
    }, [instrument]);

    // calculate EMA(20)
    const ema20 = ema()
        .options({windowSize: 20})
        .merge((d: StockData, v: number) => {
            d.ema20 = v;
        })
        .accessor((d: StockData) => d.ema20);

    const calculatedData = useMemo(
        () => (rawData.length ? ema20([...rawData]) : []),
        [rawData]
    );

    // xScale provider
    const xScaleProvider = discontinuousTimeScaleProviderBuilder().inputDateAccessor(
        (d: StockData) => d.date
    );

    const {data: chartData, xScale, xAccessor, displayXAccessor} =
        xScaleProvider(calculatedData);

    // dynamic tick format
    const xTickFormat = useMemo(() => getTickFormat(range), [range]);

    // dynamic tick count
    const xTicks = useMemo(() => {
        const w = dimensions.width;
        // About 1 tick label per 100px; clamp for sanity
        return Math.max(4, Math.floor(w / 100));
    }, [dimensions.width]);

    const xAxisTickFormat = useMemo(() => {
        return (x: any) => {
            // x is an index-like value from the discontinuous scale, not a Date.
            const idx = Math.round(Number(x));
            const row = chartData[idx];
            if (!row) return "";
            const dt = displayXAccessor(row);
            return xTickFormat(dt);
        };
    }, [chartData, displayXAccessor, xTickFormat]);

    // xExtents based on range
    const xExtents = useMemo(() => {
        if (chartData.length < 2) return [0, 1];

        const last = chartData[chartData.length - 1];
        const lastTime = last.date.getTime();

        let fromTime: number | null = null;

        switch (range) {
            case "24H":
                fromTime = lastTime - 24 * 60 * 60 * 1000;
                break;
            case "1W":
                fromTime = lastTime - 7 * 24 * 60 * 60 * 1000;
                break;
            case "1M":
                fromTime = lastTime - 30 * 24 * 60 * 60 * 1000;
                break;
            case "3M":
                fromTime = lastTime - 90 * 24 * 60 * 60 * 1000;
                break;
            case "ALL":
            default:
                return [
                    xAccessor(chartData[0]),
                    xAccessor(chartData[chartData.length - 1]),
                ];
        }

        const startIndex = chartData.findIndex(
            (d) => d.date.getTime() >= fromTime!
        );
        const start = startIndex >= 0 ? startIndex : 0;

        return [
            xAccessor(chartData[start]),
            xAccessor(chartData[chartData.length - 1]),
        ];
    }, [chartData, range, xAccessor]);

    if (!dimensions.width || !dimensions.height || chartData.length < 2) {
        return <div ref={containerRef} style={{height: 420}}/>;
    }

    // bottom margin increased for angled tick labels
    const margin = {left: 70, right: 80, top: 40, bottom: 60};
    const drawableHeight = dimensions.height - margin.top - margin.bottom;

    const priceChartHeight = Math.floor(drawableHeight * 0.7);
    const volumeChartHeight = drawableHeight - priceChartHeight;

    return (
        <div
            ref={containerRef}
            style={{
                width: "100%",
                height: "100%",
                background: "#020617",
                borderRadius: 12,
                position: "relative",
            }}
        >
            {/* ===== RANGE BUTTONS ===== */}
            <div
                style={{
                    position: "absolute",
                    top: 8,
                    right: 12,
                    display: "flex",
                    gap: 6,
                    zIndex: 10,
                }}
            >
                {(["24H", "1W", "1M", "3M", "ALL"] as TimeRange[]).map((r) => (
                    <button
                        key={r}
                        onClick={() => setRange(r)}
                        style={{
                            padding: "4px 8px",
                            fontSize: 12,
                            borderRadius: 6,
                            border: "1px solid #334155",
                            background: range === r ? "#334155" : "#020617",
                            color: "#e5e7eb",
                            cursor: "pointer",
                        }}
                    >
                        {r}
                    </button>
                ))}
            </div>

            <ChartCanvas
                seriesName={instrument}
                height={dimensions.height}
                width={dimensions.width}
                ratio={window.devicePixelRatio}
                margin={margin}
                data={chartData}
                xScale={xScale}
                xAccessor={xAccessor}
                displayXAccessor={displayXAccessor}
                xExtents={xExtents}
            >
                {/* ===== PRICE ===== */}
                <Chart
                    id={1}
                    height={priceChartHeight}
                    yExtents={(d: StockData) => [d.high, d.low]}
                >
                    <YAxis {...axisStyle} ticks={10} tickFormat={format(".2f")}/>

                    <SingleValueTooltip
                        origin={[12, 8]}
                        yAccessor={(d: StockData) => d.close}
                        yLabel="Close"
                        yDisplayFormat={format(".2f")}
                        valueFill="#e5e7eb"
                        labelFill="#94a3b8"
                    />

                    <SingleValueTooltip
                        origin={[12, 26]}
                        yAccessor={(d: StockData) => d.ema20 ?? NaN}
                        yLabel="EMA(20)"
                        yDisplayFormat={format(".2f")}
                        valueFill="#38bdf8"
                        labelFill="#94a3b8"
                    />

                    <SingleValueTooltip
                        origin={[12, 44]}
                        yAccessor={(d: StockData) => d.volume}
                        yLabel="Volume"
                        yDisplayFormat={format("~s")}
                        valueFill="#22c55e"
                        labelFill="#94a3b8"
                    />

                    <MouseCoordinateY
                        displayFormat={format(".2f")}
                        stroke="#64748b"
                        fill="#020617"
                        textFill="#e5e7eb"
                    />

                    <CandlestickSeries widthRatio={0.6}/>
                    <LineSeries
                        yAccessor={(d: StockData) => d.ema20}
                        strokeStyle="#38bdf8"
                        strokeWidth={2}
                    />
                </Chart>

                {/* ===== VOLUME ===== */}
                <Chart
                    id={2}
                    height={volumeChartHeight}
                    origin={() => [0, priceChartHeight]}
                    yExtents={(d: StockData) => d.volume}
                >
                    <XAxis
                        {...axisStyle}
                        ticks={xTicks}
                        tickFormat={xAxisTickFormat}
                    />

                    <YAxis {...axisStyle} ticks={5}/>

                    <MouseCoordinateX
                        displayFormat={timeFormat("%Y-%m-%d %H:%M")}
                        stroke="#64748b"
                        fill="#020617"
                        textFill="#e5e7eb"
                    />

                    <BarSeries
                        yAccessor={(d: StockData) => d.volume}
                        fillStyle={(d: StockData) =>
                            d.close >= d.open ? "#22c55e" : "#ef4444"
                        }
                    />
                </Chart>

                <CrossHairCursor strokeStyle="#64748b"/>
            </ChartCanvas>
        </div>
    );
}
