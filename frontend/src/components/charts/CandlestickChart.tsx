"use client";

import React, { useEffect, useRef } from "react";
import { createChart, ColorType, IChartApi, ISeriesApi } from "lightweight-charts";
import { OHLCVBar } from "@/types";

interface CandlestickChartProps {
  data: OHLCVBar[];
  height?: number;
  showVolume?: boolean;
}

export default function CandlestickChart({ data, height = 420, showVolume = true }: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data || data.length === 0) return;

    // Initialize Lightweight Chart with Light Theme Colors
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#FFFFFF" },
        textColor: "#475569",
        fontFamily: "Inter, sans-serif",
      },
      grid: {
        vertLines: { color: "#F1F5F9" },
        horzLines: { color: "#F1F5F9" },
      },
      crosshair: {
        vertLine: { color: "#94A3B8", width: 1, style: 2 },
        horzLine: { color: "#94A3B8", width: 1, style: 2 },
      },
      rightPriceScale: {
        borderColor: "#E2E8F0",
      },
      timeScale: {
        borderColor: "#E2E8F0",
        timeVisible: true,
        secondsVisible: false,
      },
      width: chartContainerRef.current.clientWidth,
      height: height,
    });

    chartRef.current = chart;

    // 1. Candlestick Series
    const candleSeries = chart.addCandlestickSeries({
      upColor: "#0D824D",
      downColor: "#D32F2F",
      borderVisible: false,
      wickUpColor: "#0D824D",
      wickDownColor: "#D32F2F",
    });

    const candleData = data.map((d) => ({
      time: d.time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));
    candleSeries.setData(candleData);

    // 2. SMA 20 Line Overlay
    const sma20Series = chart.addLineSeries({
      color: "#2563EB",
      lineWidth: 1,
      title: "SMA 20",
    });
    const sma20Data = data
      .filter((d) => d.sma_20 !== null && d.sma_20 !== undefined)
      .map((d) => ({ time: d.time, value: d.sma_20 as number }));
    if (sma20Data.length > 0) sma20Series.setData(sma20Data);

    // 3. SMA 50 Line Overlay
    const sma50Series = chart.addLineSeries({
      color: "#C5A059",
      lineWidth: 1,
      title: "SMA 50",
    });
    const sma50Data = data
      .filter((d) => d.sma_50 !== null && d.sma_50 !== undefined)
      .map((d) => ({ time: d.time, value: d.sma_50 as number }));
    if (sma50Data.length > 0) sma50Series.setData(sma50Data);

    // 4. Volume Histogram (Optional)
    if (showVolume) {
      const volumeSeries = chart.addHistogramSeries({
        color: "#CBD5E1",
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

      const volumeData = data.map((d) => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? "rgba(13, 130, 77, 0.25)" : "rgba(211, 47, 47, 0.25)",
      }));
      volumeSeries.setData(volumeData);
    }

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [data, height, showVolume]);

  return (
    <div className="w-full relative">
      <div className="flex items-center gap-4 mb-2 text-xs font-mono">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-financial-gain inline-block"></span>
          <span className="text-slate-600">Bullish</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-financial-loss inline-block"></span>
          <span className="text-slate-600">Bearish</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-blue-600 inline-block"></span>
          <span className="text-slate-600">SMA 20</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-gold inline-block"></span>
          <span className="text-slate-600">SMA 50</span>
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full rounded-lg border border-border overflow-hidden shadow-sm" />
    </div>
  );
}
