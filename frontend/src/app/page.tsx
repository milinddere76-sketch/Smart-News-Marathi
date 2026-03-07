import React from 'react';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="marathi-gradient text-white p-4 shadow-lg sticky top-0 z-50">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-3xl font-bold">स्मार्ट न्यूज मराठी</h1>
          <nav className="hidden md:flex space-x-6 font-medium">
            <a href="#" className="hover:text-yellow-400">होम</a>
            <a href="#" className="hover:text-yellow-400">महाराष्ट्र</a>
            <a href="#" className="hover:text-yellow-400">भारत</a>
            <a href="#" className="hover:text-yellow-400">मनोरंजन</a>
            <a href="#" className="hover:text-yellow-400">खेळ</a>
          </nav>
          <div className="bg-red-600 px-4 py-1 rounded-full text-sm animate-pulse border border-white font-bold">
            लाईव्ह TV
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto mt-8 px-4">
        {/* Hero Section */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Live Video Player Placeholder */}
          <div className="lg:col-span-2">
            <div className="bg-black aspect-video rounded-xl shadow-2xl flex items-center justify-center relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
              <div className="text-white text-center z-10">
                <p className="text-xl mb-4">24x7 लाईव्ह न्यूज सुरू आहे...</p>
                <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center mx-auto cursor-pointer hover:scale-110 transition-transform">
                   <svg className="w-8 h-8 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                </div>
              </div>
              <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 text-xs font-bold rounded flex items-center">
                <span className="w-2 h-2 bg-white rounded-full mr-2 animate-ping"></span>
                LIVE
              </div>
            </div>
            
            <div className="mt-6">
              <h2 className="text-2xl font-bold border-b-4 border-red-600 inline-block mb-4">ठळक बातम्या</h2>
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow flex gap-4">
                    <div className="w-32 h-24 bg-gray-200 rounded shrink-0"></div>
                    <div>
                      <h3 className="text-lg font-bold">महाराष्ट्रातील राजकीय घडामोडींना वेग; नवीन निर्णयाची शक्यता</h3>
                      <p className="text-gray-600 text-sm mt-2">मुंबई: आज झालेल्या बैठकीत महत्त्वाचे निर्णय घेण्यात आले असून...</p>
                      <span className="text-xs text-red-600 mt-2 block">2 मिनिटांपूर्वी</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-xl shadow-lg border-t-8 border-blue-800">
              <h3 className="text-xl font-bold mb-4">ताज्या बातम्या</h3>
              <ul className="space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <li key={i} className="border-b pb-2 hover:text-blue-600 cursor-pointer">
                    • पुण्यात पावसाचा जोर वाढला, नागरिकांना सतर्कतेचा इशारा
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-yellow-50 p-6 rounded-xl border border-yellow-200 shadow-sm">
              <h3 className="text-xl font-bold mb-4 text-yellow-800">जाहिरात</h3>
              <div className="bg-gray-200 w-full h-40 rounded flex items-center justify-center text-gray-400">
                तुमची जाहीरात येथे द्या
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer Ticker */}
      <footer className="fixed bottom-0 w-full bg-black text-white py-2 z-50 overflow-hidden">
        <div className="whitespace-nowrap animate-marquee">
          <span className="mx-8">| मुंबई: मुसळधार पावसाचा इशारा |</span>
          <span className="mx-8">| महाविकास आघाडीची महत्त्वाची बैठक आज |</span>
          <span className="mx-8">| भारताची अवकाश क्षेत्रात मोठी झेप |</span>
          <span className="mx-8">| शेअर बाजारात मोठी तेजी, सेन्सेक्स वधारला |</span>
        </div>
      </footer>
      
    </div>
  );
}
