export const metadata = {
  title: "Sentinel Square Dashboard",
  description: "Command center for autonomous Binance Square content agent",
};

import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
