"use client";

import React, { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi, CandlestickData, HistogramData, UTCTimestamp } from "lightweight-charts";
import { OHLCV } from "@/types";

export interface CandlestickChartProps {
  data: OHLCV[];
  height?: number;
  className?: string;
  currency?: string;
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  data,
  height = 400,
  className,
}) => {
  const chartContainerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Initialize Lightweight Chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { color: "#FFFFFF" },
        textColor: "#6B756E",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: "#F0F2ED" },
        horzLines: { color: "#F0F2ED" },
      },
      crosshair: {
        vertLine: { color: "#12372A", width: 1, style: 2 },
        horzLine: { color: "#12372A", width: 1, style: 2 },
      },
      rightPriceScale: {
        borderColor: "#E3E7E3",
        scaleMargins: {
          top: 0.1,
          bottom: 0.25,
        },
      },
      timeScale: {
        borderColor: "#E3E7E3",
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // Add Candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: "#0D824D",
      downColor: "#D32F2F",
      borderUpColor: "#0D824D",
      borderDownColor: "#D32F2F",
      wickUpColor: "#0D824D",
      wickDownColor: "#D32F2F",
    });

    // Add Volume histogram series
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: {
        type: "volume",
      },
      priceScaleId: "", // overlay
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    // Handle Resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [height]);

  useEffect(() => {
    if (!candleSeriesRef.current || !volumeSeriesRef.current || !data || data.length === 0) {
      return;
    }

    // Format OHLCV data for Lightweight charts (sorted ascending by timestamp)
    const sortedData = [...data].sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    const candleData: CandlestickData[] = sortedData.map((d) => ({
      time: (Math.floor(new Date(d.timestamp).getTime() / 1000) as UTCTimestamp),
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    const volumeData: HistogramData[] = sortedData.map((d) => ({
      time: (Math.floor(new Date(d.timestamp).getTime() / 1000) as UTCTimestamp),
      value: d.volume,
      color: d.close >= d.open ? "rgba(13, 130, 77, 0.2)" : "rgba(211, 47, 47, 0.2)",
    }));

    candleSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volumeData);
    chartRef.current?.timeScale().fitContent();
  }, [data]);

  return (
    <div className={className}>
      <div ref={chartContainerRef} className="w-full rounded-lg overflow-hidden" />
    </div>
  );
};
