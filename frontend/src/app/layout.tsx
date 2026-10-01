import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/hooks/useAuth";
import { ToastProvider } from "@/components/common/Toast";
import { MarketWebSocketProvider } from "@/providers/MarketWebSocketProvider";

export const metadata: Metadata = {
  title: "MarketMind AI | AI-Powered Stock Market Intelligence",
  description:
    "Institutional-grade financial intelligence, LangGraph research agent, SEC 10-K RAG, ML anomaly detection, and scenario stress testing for Indian (NSE/BSE) and Global markets.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-background text-content font-sans antialiased min-h-screen">
        <AuthProvider>
          <MarketWebSocketProvider>
            <ToastProvider>
              {children}
            </ToastProvider>
          </MarketWebSocketProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

