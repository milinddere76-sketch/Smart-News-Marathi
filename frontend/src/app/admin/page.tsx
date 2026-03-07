import React from 'react';

export default function AdminDashboard() {
  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h2 className="text-xl font-bold text-blue-400">स्मार्ट न्यूज Admin</h2>
        </div>
        <nav className="flex-grow p-4 space-y-2">
          <a href="#" className="block py-2.5 px-4 rounded transition duration-200 bg-blue-600">डॅशबोर्ड</a>
          <a href="#" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-slate-700">बातम्या व्यवस्थापन</a>
          <a href="#" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-slate-700">जाहिरात केंद्र</a>
          <a href="#" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-slate-700">स्ट्रीम स्थिती</a>
          <a href="#" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-slate-700">सेटिंग्ज</a>
        </nav>
        <div className="p-4 border-t border-slate-700 text-sm text-slate-400">
          v1.0.0
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="bg-white shadow-sm p-4 flex justify-between items-center">
          <h1 className="text-2xl font-semibold">नियंत्रण कक्ष (Control Room)</h1>
          <div className="flex items-center space-x-4">
            <span className="text-green-500 flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              स्ट्रीम सुरू आहे
            </span>
            <div className="w-10 h-10 bg-slate-200 rounded-full"></div>
          </div>
        </header>

        <div className="p-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[
              { label: "आजच्या बातम्या", val: "24", icon: "📰" },
              { label: "सक्रिय जाहिराती", val: "12", icon: "💰" },
              { label: "लाईव्ह दर्शक", val: "1.2k", icon: "👁️" },
              { label: "जाहिरात उत्पन्न", val: "₹15,000", icon: "📈" }
            ].map((stat, i) => (
              <div key={i} className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-blue-500">
                <div className="text-3xl mb-2">{stat.icon}</div>
                <div className="text-gray-500 text-sm">{stat.label}</div>
                <div className="text-2xl font-bold">{stat.val}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* News Queue */}
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <h3 className="text-xl font-bold mb-4 flex justify-between">
                प्रलंबित बातम्या
                <span className="text-sm bg-yellow-100 text-yellow-800 px-2 py-1 rounded">अॅक्शन आवश्यक</span>
              </h3>
              <div className="space-y-4">
                {[
                  "मुंबई विमानतळावर मोठी कारवाई, सोने जप्त",
                  "राज्यात नवीन शैक्षणिक धोरण लागू",
                  "हवामान विभागाचा 'ऑरेंज अलर्ट'"
                ].map((news, i) => (
                  <div key={i} className="flex items-center justify-between border-b pb-4">
                    <span className="font-medium">{news}</span>
                    <div className="space-x-2 flex">
                      <button className="bg-green-100 text-green-700 px-3 py-1 rounded-md text-sm hover:bg-green-200">मंजूर करा</button>
                      <button className="bg-red-100 text-red-700 px-3 py-1 rounded-md text-sm hover:bg-red-200">रद्द करा</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Ad Management */}
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <h3 className="text-xl font-bold mb-4">जाहिरात व्यवस्थापन</h3>
              <div className="space-y-4">
                <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition">
                  + नवीन जाहिरात अपलोड करा
                </button>
                <div className="mt-4">
                  <h4 className="text-sm font-semibold text-gray-400 mb-2 uppercase">सध्या सुरू असलेल्या जाहिराती</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between p-3 bg-gray-50 rounded italic text-sm">
                      <span>1. साकेत हॉस्पिटल (30s)</span>
                      <span className="text-blue-500">सुरू आहे</span>
                    </div>
                    <div className="flex justify-between p-3 bg-gray-50 rounded italic text-sm">
                      <span>2. स्टार कोचींग क्लासेस (15s)</span>
                      <span className="text-blue-500">सुरू आहे</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
