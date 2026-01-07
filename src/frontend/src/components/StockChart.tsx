import React, { useEffect, useMemo, useRef, useState } from "react";
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
import { timeFormat } from "d3-time-format";
import { format } from "d3-format";


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


const axisStyle = {
    stroke: "#475569",
    tickStroke: "#475569",
    tickLabelFill: "#e5e7eb",
};


export default function StockChart({ instrument }: StockChartProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [rawData, setRawData] = useState<StockData[]>([]);


    // handle resize
    useEffect(() => {
        if (!containerRef.current) return;

        const observer = new ResizeObserver(entries => {
            const { width, height } = entries[0].contentRect;
            setDimensions({ width, height });
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
                    { signal: controller.signal }
                );

                const parsed: StockData[] = res.data
                    .map((item: any) => {
                        const date = new Date(item.start_time);
                        if (isNaN(date.getTime())) return null;

                        return {
                            date,
                            open: +item.open_price,
                            high: +item.high_price,
                            low: +item.low_price,
                            close: +item.close_price,
                            volume: Number(item.volume) || 0,
                        };
                    })
                    .filter((d : StockData): d is StockData => d !== null)
                    .sort((a: { date: { getTime: () => number; }; }, b: { date: { getTime: () => number; }; }) => a.date.getTime() - b.date.getTime());

                setRawData(parsed);
            } catch (err: any) {
                if (err.code === "ERR_CANCELED") return;
                throw err;
            }
        }

        fetchData();
        return () => controller.abort();
    }, [instrument]);

    // calculate indicators
    const ema20 = ema()
        .options({ windowSize: 20 })
        .merge((d: StockData, v: number) => {
            d.ema20 = v;
        })
        .accessor((d: StockData) => d.ema20);

    const calculatedData = useMemo(
        () => (rawData.length ? ema20([...rawData]) : []),
        [rawData]
    );

    // prepare chart data
    const xScaleProvider =
        discontinuousTimeScaleProviderBuilder()
            .inputDateAccessor(d => d.date);

    const {
        data: chartData,
        xScale,
        xAccessor,
        displayXAccessor,
    } = xScaleProvider(calculatedData);

    if (!dimensions.width || !dimensions.height || chartData.length < 2) {
        return <div ref={containerRef} style={{ height: 420 }} />;
    }

    const xExtents = [
        xAccessor(chartData[0]),
        xAccessor(chartData[chartData.length - 1]),
    ];

    const priceChartHeight = Math.floor(dimensions.height * 0.7);
    const volumeChartHeight = Math.floor(dimensions.height * 0.3);


    return (
        <div
            ref={containerRef}
            style={{
                width: "100%",
                height: "100%",
                background: "#020617",
                borderRadius: 12,
            }}
        >
            <ChartCanvas
                seriesName={instrument}
                height={dimensions.height}
                width={dimensions.width}
                ratio={window.devicePixelRatio}
                margin={{ left: 70, right: 80, top: 40, bottom: 40 }}
                data={chartData}
                xScale={xScale}
                xAccessor={xAccessor}
                displayXAccessor={displayXAccessor}
                xExtents={xExtents}
            >
                {/* ================= PRICE CHART ================= */}
                <Chart
                    id={1}
                    height={priceChartHeight}
                    yExtents={d => [d.high, d.low]}
                >
                    <XAxis
                        {...axisStyle}
                        ticks={20}
                        tickFormat={timeFormat("%m-%d %H:%M")}
                    />

                    <YAxis
                        {...axisStyle}
                        ticks={10}
                        tickFormat={format(".2f")}
                    />

                    {/* ===== TOP-LEFT LEGEND ===== */}
                    <SingleValueTooltip
                        origin={[12, 8]}
                        yAccessor={d => d.close}
                        yLabel="Close"
                        yDisplayFormat={format(".2f")}
                        valueFill="#e5e7eb"
                        labelFill="#94a3b8"
                    />

                    <SingleValueTooltip
                        origin={[12, 26]}
                        yAccessor={d => d.ema20}
                        yLabel="EMA(20)"
                        yDisplayFormat={format(".2f")}
                        valueFill="#38bdf8"
                        labelFill="#94a3b8"
                    />

                    <SingleValueTooltip
                        origin={[12, 44]}
                        yAccessor={d => d.volume}
                        yLabel="Volume"
                        yDisplayFormat={format("~s")}
                        valueFill="#22c55e"
                        labelFill="#94a3b8"
                    />

                    <MouseCoordinateX
                        displayFormat={timeFormat("%Y-%m-%d %H:%M")}
                        stroke="#64748b"
                        fill="#020617"
                        textFill="#e5e7eb"
                    />

                    <MouseCoordinateY
                        displayFormat={format(".2f")}
                        stroke="#64748b"
                        fill="#020617"
                        textFill="#e5e7eb"
                    />

                    <CandlestickSeries widthRatio={0.6} />

                    <LineSeries
                        yAccessor={d => d.ema20}
                        strokeStyle="#38bdf8"
                        strokeWidth={2}
                    />
                </Chart>

                {/* ================= VOLUME CHART ================= */}
                <Chart
                    id={2}
                    height={volumeChartHeight}
                    origin={() => [0, priceChartHeight + 50]}
                    yExtents={d => d.volume}
                >
                    <YAxis {...axisStyle} ticks={5} />

                    <BarSeries
                        yAccessor={d => d.volume}
                        fillStyle={d =>
                            d.close >= d.open ? "#22c55e" : "#ef4444"
                        }
                    />
                </Chart>

                <CrossHairCursor stroke="#64748b" />
            </ChartCanvas>
        </div>
    );
}
