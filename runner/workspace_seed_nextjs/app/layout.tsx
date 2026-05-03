import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Task Tracker",
  description: "A simple task management app",
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
