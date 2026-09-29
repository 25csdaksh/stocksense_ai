import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/ui/Navbar";
import Sidebar from "@/components/ui/Sidebar";

export const metadata: Metadata = {
  title: "MARKETMIND AI — Stock Market Intelligence & Scenario Platform",
  description:
    "AI-Powered Stock Market Intelligence, RAG Knowledge Engine, and Scenario Analysis Platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-slate-900 flex flex-col font-sans">
        <Navbar />
        <div className="flex-1 flex overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
