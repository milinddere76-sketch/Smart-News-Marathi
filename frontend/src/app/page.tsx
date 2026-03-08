'use client';

import { useState, useEffect } from 'react';

// Smart News Marathi — Professional Broadcast Studio Frontend
// Dark, broadcast-grade design for 24x7 live news

// ── Configuration ────────────────────────────────────────────────────────────
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const YOUTUBE_ID = process.env.NEXT_PUBLIC_YOUTUBE_ID || '';
const CATEGORIES = ['महाराष्ट्र', 'भारत', 'जग', 'राजकारण', 'अर्थ', 'खेळ', 'मनोरंजन', 'तंत्रज्ञान'];

const TICKER_ITEMS = [
  'मुंबई: मुसळधार पाऊस; अनेक भागात पूरस्थिती',
  'पुणे: राजकीय बैठकीत महत्त्वाचे निर्णय',
  'नागपूर: उद्योग परिषदेत 5000 कोटींचे करार',
  'शेअर बाजार: सेन्सेक्स आजवरच्या उच्चांकावर',
  'भारत-ऑस्ट्रेलिया: तिसरी कसोटी भारत जिंकला',
  'दिल्ली: संसदेत महत्त्वाचे विधेयक मंजूर',
];

const BREAKING = 'ताज्या: महाराष्ट्र सरकारकडून नवीन धोरण जाहीर — शेतकऱ्यांना मोठा दिलासा';

const SIDEBAR_HEADLINES = [
  { cat: 'महाराष्ट्र', text: 'राज्यात नवीन शैक्षणिक धोरण लागू होणार' },
  { cat: 'राजकारण', text: 'विधानसभेत विरोधी पक्षाचे जोरदार आंदोलन' },
  { cat: 'अर्थ', text: 'जीएसटी महसुलात 18% वाढ; अर्थमंत्री प्रसन्न' },
  { cat: 'तंत्रज्ञान', text: 'AI स्टार्टअपने जागतिक करार साध्य केला' },
  { cat: 'खेळ', text: 'IPL 2025: मुंबई इंडियन्स विजयी' },
  { cat: 'जग', text: 'UN परिषदेत भारताचा महत्त्वाचा प्रस्ताव' },
];


export default function StudioPage() {
  const [latestVideo, setLatestVideo] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchLatestVideo = async () => {
    try {
      const resp = await fetch(`${API_BASE}/latest-video`);
      const data = await resp.json();
      if (data.filename) {
        setLatestVideo(data.filename);
      }
    } catch (err) {
      console.error('Failed to fetch latest video:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestVideo();
    // Refresh every minute to check for new clips
    const timer = setInterval(fetchLatestVideo, 60000);
    return () => clearInterval(timer);
  }, []);

  const tickerLine = TICKER_ITEMS.join('  |  ');

  return (
    <div className="studio-root">

      {/* ── BREAKING NEWS ALERT BANNER ─────────────────────────────────────── */}
      <div className="breaking-banner">
        <span className="breaking-label">ब्रेकिंग</span>
        <span className="breaking-text">{BREAKING}</span>
      </div>

      {/* ── TOP NAVIGATION ─────────────────────────────────────────────────── */}
      <header className="studio-header">
        <div className="studio-header-inner">

          {/* Logo */}
          <div className="studio-logo">
            <div className="logo-icon">SNM</div>
            <div>
              <div className="logo-name">स्मार्ट न्यूज मराठी</div>
              <div className="logo-tagline">सत्य · निर्भय · निष्पक्ष</div>
            </div>
          </div>

          {/* Category Nav */}
          <nav className="studio-nav">
            {CATEGORIES.map((cat) => (
              <a key={cat} href="#" className="studio-nav-link">{cat}</a>
            ))}
          </nav>

          {/* Live badge + date */}
          <div className="header-right">
            <div className="live-pill">
              <span className="live-dot" />
              LIVE
            </div>
          </div>
        </div>
      </header>

      {/* ── TICKER BAR ─────────────────────────────────────────────────────── */}
      <div className="studio-ticker-bar">
        <div className="ticker-label-box">ताज्या बातम्या</div>
        <div className="ticker-overflow">
          <div className="ticker-scroll">
            {tickerLine}  •  {tickerLine}
          </div>
        </div>
      </div>

      {/* ── MAIN CONTENT ─────────────────────────────────────────────────────*/}
      <main className="studio-main">

        {/* ── Left: Content Zone ───────────────────────────────────────────── */}
        <section className="studio-primary">

          {/* 📺 YT LIVE PLAYER ────────────────────────────────────────────── */}
          <div className="section-header">
            <h2 className="section-title">
              <span className="section-title-bar" />
              लाईव्ह ब्रॉडकास्ट
            </h2>
          </div>
          
          <div className="studio-player-wrap">
            {YOUTUBE_ID ? (
              <iframe
                className="studio-iframe"
                src={`https://www.youtube.com/embed/live_stream?channel=${YOUTUBE_ID}&autoplay=1&mute=1`}
                title="Smart News Marathi Live"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            ) : latestVideo ? (
              /* Pseudo-Live Player (Fallback for when YouTube Stream Key is missing) */
              <video 
                className="studio-iframe" 
                autoPlay 
                muted 
                loop 
                playsInline
                key={`pseudo-${latestVideo}`}
                poster="/media/assets/anchor.jpg"
              >
                <source src={`${API_BASE}/media/video/${latestVideo}`} type="video/mp4" />
                <div className="player-placeholder">
                  <p>Your browser does not support the video tag.</p>
                </div>
              </video>
            ) : (
              <div className="player-placeholder">
                <div className="placeholder-inner">
                  <div className="placeholder-spinner" />
                  <p className="placeholder-title">स्मार्ट न्यूज मराठी</p>
                  <p className="placeholder-sub">लाईव्ह स्ट्रीमिंग सुरू होत आहे…</p>
                </div>
              </div>
            )}
            <div className="player-overlay-live">
              <span className="live-dot" />LIVE
            </div>
          </div>

          {/* 🎬 LATEST AI PREVIEW ──────────────────────────────────────────── */}
          <div className="section-header section-header-ai">
            <h2 className="section-title section-title--gold">
              <span className="section-title-bar section-title-bar--gold" />
              नवीनतम AI बुलेटीन
            </h2>
            <span className="ai-badge">AI GENERATED</span>
          </div>

          <div className="latest-preview-card">
            {latestVideo ? (
              <div className="preview-player-wrap">
                <video 
                  controls 
                  className="preview-video"
                  key={latestVideo} // Force re-mount when video changes
                  poster="/media/assets/anchor.jpg"
                >
                  <source src={`${API_BASE}/media/video/${latestVideo}`} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
                <div className="preview-info">
                  <span className="preview-tag">सर्वात नवीन</span>
                  <h3 className="preview-title">स्मार्ट न्यूज विशेष बुलेटीन</h3>
                  <p className="preview-desc">AI अँकरद्वारे सादर केलेल्या आजच्या ताज्या बातम्यांचे सविस्तर विश्लेषण.</p>
                </div>
              </div>
            ) : (
              <div className="preview-empty">
                {loading ? 'माहिती मिळवत आहे...' : 'सध्या कोणतेही नवीन बुलेटीन उपलब्ध नाही.'}
              </div>
            )}
          </div>

          {/* 📰 FEATURED GRID ─────────────────────────────────────────────── */}
          <div className="featured-grid">
            <h2 className="section-title">
              <span className="section-title-bar" />
              ठळक बातम्या
            </h2>
            <div className="featured-cards">
              {[
                { cat: 'महाराष्ट्र', title: 'राज्यात नव्या रोजगार योजनेची घोषणा; 50,000 जागा', time: '3 मि' },
                { cat: 'राजकारण', title: 'मुख्यमंत्र्यांनी घेतली मंत्रिमंडळ बैठक; मोठे निर्णय', time: '12 मि' },
                { cat: 'अर्थ', title: 'शेअर बाजारात 800 अंकांची तेजी; गुंतवणूकदार खूश', time: '28 मि' },
              ].map((story, i) => (
                <div key={i} className="featured-card">
                  <div className="featured-thumb">
                    <span className="thumb-cat">{story.cat}</span>
                  </div>
                  <div className="featured-body">
                    <h3 className="featured-title">{story.title}</h3>
                    <span className="featured-time">{story.time} पूर्वी</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Right: Sidebar ────────────────────────────────────────────────*/}
        <aside className="studio-sidebar">

          {/* Latest News */}
          <div className="sidebar-widget">
            <h3 className="widget-title">
              <span className="widget-bar" />
              ताज्या बातम्या
            </h3>
            <ul className="widget-list">
              {SIDEBAR_HEADLINES.map((h, i) => (
                <li key={i} className="widget-item">
                  <span className="widget-cat">{h.cat}</span>
                  <a href="#" className="widget-link">{h.text}</a>
                </li>
              ))}
            </ul>
          </div>

          {/* AI Status Widget */}
          <div className="sidebar-widget ai-widget">
            <h3 className="widget-title">
              <span className="widget-bar widget-bar--gold" />
              AI Studio Status
            </h3>
            <div className="ai-status-row">
              <span className="status-dot status-dot--green" />
              <span>News Scraper</span>
              <span className="status-val">Active</span>
            </div>
            <div className="ai-status-row">
              <span className="status-dot status-dot--green" />
              <span>Script AI (Gemini)</span>
              <span className="status-val">Ready</span>
            </div>
            <div className="ai-status-row">
              <span className="status-dot status-dot--green" />
              <span>Voice TTS</span>
              <span className="status-val">Ready</span>
            </div>
            <div className="ai-status-row">
              <span className="status-dot status-dot--yellow" />
              <span>Video Compositor</span>
              <span className="status-val">Processing</span>
            </div>
            <div className="ai-status-row">
              <span className="status-dot status-dot--green" />
              <span>YouTube Stream</span>
              <span className="status-val">Live</span>
            </div>
          </div>

          {/* Ad Slot */}
          <div className="sidebar-widget ad-widget">
            <div className="ad-label">जाहिरात</div>
            <div className="ad-placeholder">तुमची जाहीरात येथे द्या</div>
          </div>
        </aside>
      </main>

      {/* ── FOOTER ───────────────────────────────────────────────────────────*/}
      <footer className="studio-footer">
        <div className="footer-inner">
          <div className="footer-brand">स्मार्ट न्यूज मराठी © 2025</div>
          <div className="footer-links">
            <a href="#">About</a>
            <a href="#">Contact</a>
            <a href="#">Privacy</a>
          </div>
          <div className="footer-note">Powered by AI · 24x7 Live Broadcast</div>
        </div>
      </footer>
    </div>
  );
}
