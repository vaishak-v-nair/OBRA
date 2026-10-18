import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import { Shell } from "@/components/shell";
import "./globals.css";
export const metadata: Metadata = { title: "ORBA · Your development workspace", description: "A local workspace for your next software project.", referrer: "no-referrer" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" suppressHydrationWarning><body><Providers><Shell>{children}</Shell></Providers></body></html>;
}
