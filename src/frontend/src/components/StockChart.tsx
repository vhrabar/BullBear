import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import {
    ChartCanvas,
    Chart,
    CandlestickSeries,
    LineSeries,
    BarSeries,
    XAxis,
    YAxis,
    CrossHairCursor,
    MouseCoordinateX,
    MouseCoordinateY,
    OHLCTooltip,
    discontinuousTimeScaleProviderBuilder,
    lastVisibleItemBasedZoomAnchor,
    ema,
} from "react-financial-charts";
import { format } from "d3-format";
import { timeFormat } from "d3-time-format";

import "./StockChart.css";

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

export default function StockChart({ instrument }: StockChartProps) {
    const [data, setData] = useState<StockData[]>([]);
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

    // Measure container size
    useEffect(() => {
        if (!containerRef.current) return;
        const resizeObserver = new ResizeObserver((entries) => {
            for (let entry of entries) {
                const { width, height } = entry.contentRect;
                setDimensions({ width, height });
            }
        });
        resizeObserver.observe(containerRef.current);
        return () => resizeObserver.disconnect();
    }, []);

    // Fetch data
    useEffect(() => {
        const controller = new AbortController();

        async function fetchData() {
            try {
                const res = await axios.get(
                    `/api/trading/instrument-data/?instrument=${instrument}`,
                    { signal: controller.signal }
                );
                res.data.forEach((item, i) => {
    const parsedDate = new Date(item.start_time);
    console.log(`Index ${i}: "${item.start_time}" =>`, parsedDate);
});

                const chartData: StockData[] = res.data
                    .map((item: any) => ({
                        date: new Date(item.start_time),
                        open: Number(item.open_price),
                        high: Number(item.high_price),
                        low: Number(item.low_price),
                        close: Number(item.close_price),
                        volume: Number(item.volume) || 0,
                    }))
                    .filter((d) => d.date instanceof Date && !isNaN(d.date.getTime()))
                    .sort((a, b) => a.date.getTime() - b.date.getTime());

                setData(chartData);
            } catch (err: any) {
                if (axios.isCancel(err)) return;
                console.error("Error fetching chart data:", err);
            }
        }

        fetchData();
        return () => controller.abort();
    }, [instrument]);

    // Show loading if container not measured or no data
    if (dimensions.width === 0 || dimensions.height === 0 || data.length < 2) {
        return <div ref={containerRef} style={{ width: "100%", height: "400px" }}>Loading chart...</div>;
    }

    // Calculate EMA
    const ema20 = ema()
        .id(1)
        .options({ windowSize: 20 })
         .merge((d: StockData, c: number) => { d.ema20 = c; })
        .accessor((d: StockData) => d.ema20);

    console.log("Original data size:", data.length);
    const calculatedData = ema20(data);
    console.log("Calculated data size:", calculatedData.length);

    const xScaleProvider = discontinuousTimeScaleProviderBuilder()
        .inputDateAccessor((d: StockData) => d.date);

    const { data: chartData, xScale, xAccessor, displayXAccessor } = xScaleProvider(calculatedData);

    const startIndex = Math.max(chartData.length - 100, 0);
    const endIndex = chartData.length - 1;
    const xExtents = [xAccessor(chartData[startIndex]), xAccessor(chartData[endIndex])];

    // Calculate sub-chart heights
    const priceChartHeight = Math.floor(dimensions.height * 0.7);
    const volumeChartHeight = Math.floor(dimensions.height * 0.25);

    return (
        <div ref={containerRef} style={{ width: "100%", height: "100%" }} className="candlestick-chart-container">
            <ChartCanvas
                height={dimensions.height}
                width={dimensions.width}
                ratio={window.devicePixelRatio}
                margin={{ left: 60, right: 60, top: 20, bottom: 30 }}
                seriesName={instrument}
                data={chartData}
                xScale={xScale}
                xAccessor={xAccessor}
                displayXAccessor={displayXAccessor}
                xExtents={xExtents}
                zoomAnchor={lastVisibleItemBasedZoomAnchor}
            >
                {/* PRICE CHART */}
                <Chart id={1} height={priceChartHeight} yExtents={(d: StockData) => [d.high, d.low]}>
                    <XAxis stroke="#374151" tickStroke="#9ca3af" fontSize={11} />
                    <YAxis stroke="#374151" tickStroke="#9ca3af" fontSize={11} />
                    <MouseCoordinateX displayFormat={timeFormat("%Y-%m-%d %H:%M")} />
                    <MouseCoordinateY displayFormat={format(".2f")} />
                    <CandlestickSeries
                        fill={(d: StockData) => (d.close > d.open ? "#22c55e" : "#ef4444")}
                        wickStroke={(d: StockData) => (d.close > d.open ? "#22c55e" : "#ef4444")}
                        width={8}
                    />
                    <LineSeries yAccessor={(d: StockData) => d.ema20} stroke="#38bdf8" strokeWidth={1.5} />
                    <OHLCTooltip origin={[8, 16]} />
                </Chart>

                {/* VOLUME CHART */}
                <Chart
                    id={2}
                    height={volumeChartHeight}
                    origin={(w, h) => [0, priceChartHeight]}
                    yExtents={(d: StockData) => d.volume}
                >
                    <YAxis ticks={3} tickFormat={(v) => `${(v / 1_000_000).toFixed(1)}M`} stroke="#374151" tickStroke="#9ca3af" fontSize={10} />
                    <BarSeries
                        yAccessor={(d: StockData) => d.volume}
                        fill={(d: StockData) =>
                            d.close > d.open ? "rgba(34,197,94,0.45)" : "rgba(239,68,68,0.45)"
                        }
                    />
                </Chart>

                <CrossHairCursor stroke="#e5e7eb" />
            </ChartCanvas>
        </div>
    );
}
