import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI WebsScraper',
  description: 'A powerful AI-driven web scraper that leverages FastAPI and Googles Generative AI to intelligently extract and process structured data from websites. Designed for flexibility, automation, and integration into modern data workflows.',
  generator: 'Next.js',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
