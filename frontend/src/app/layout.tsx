import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "VartaPravah Admin",
  description: "Secure control dashboard for the VartaPravah live stream.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased font-sans bg-[#0a0f1e] text-white">
        {children}
      </body>
    </html>
  );
}
