export const metadata = {
  title: "Sentinel-Square | Autonomous Content & Trading Engine",
  description: "Official real-time monitoring dashboard for the Sentinel-Square autonomous Binance Square agent. Maximizing Write-to-Earn rewards and yield optimization.",
  keywords: ["Sentinel-Square", "Binance Square", "Write to Earn", "Crypto Analyst", "Yield Optimization", "Autonomous Trading"],
  authors: [{ name: "MOMIGI 2026" }],
  icons: {
    icon: "/logo.png",
    apple: "/logo.png",
  },
  openGraph: {
    title: "Sentinel-Square | Autonomous Analyst Dashboard",
    description: "Real-time alpha and yield monitoring for Sentinel-Square.",
    url: "https://squareautomation.vercel.app",
    siteName: "Sentinel-Square",
    images: [
      {
        url: "/logo.png",
        width: 1200,
        height: 630,
      },
    ],
    locale: "en_US",
    type: "website",
  },
};

import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="relative">
        {/* Aura Background Blobs */}
        <div className="aura-blob bg-cyan-500 w-[500px] h-[500px] -top-64 -left-64" />
        <div className="aura-blob bg-purple-500 w-[400px] h-[400px] top-1/2 -right-32 delay-1000" />
        <div className="aura-blob bg-blue-500 w-[600px] h-[600px] -bottom-96 left-1/2 -translate-x-1/2 opacity-10" />
        
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  );
}
