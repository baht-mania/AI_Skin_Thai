import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "K-Sun Shield by FULLMOON",
  description: "AI 피부 진단으로 나만의 K-뷰티 루틴을 찾아보세요.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
