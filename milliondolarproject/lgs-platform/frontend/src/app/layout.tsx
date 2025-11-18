import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LGS Adaptive Platform",
  description: "Adaptive learning platform for LGS exam preparation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
