import './globals.css';

export const metadata = {
  title: 'स्मार्ट न्यूज मराठी | 24x7 Live News',
  description: 'महाराष्ट्रातील सर्वात विश्वासू 24x7 AI-powered मराठी बातम्यांचे चॅनल.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="mr">
      <body>{children}</body>
    </html>
  );
}
