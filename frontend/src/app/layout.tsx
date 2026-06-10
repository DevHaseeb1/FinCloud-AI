import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppProviders } from "@/components/app/AppProviders";
import { AppShell } from "@/components/app/AppShell";
import { PageTransition } from "@/components/shell/PageTransition";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "700", "800"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "FinCloud-AI",
  description: "FinOps analytics with anomaly detection, forecasting, and recommendations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <TooltipProvider>
          <AppProviders>
            <AppShell>
              <PageTransition>{children}</PageTransition>
            </AppShell>
          </AppProviders>
        </TooltipProvider>
      </body>
    </html>
  );
}
