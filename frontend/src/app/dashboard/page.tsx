"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { LogOut, UploadCloud, Video, AlertCircle, PlaySquare } from "lucide-react";

export default function Dashboard() {
  const router = useRouter();
  const [queue, setQueue] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchQueue();
    // Poll queue every 5 seconds
    const interval = setInterval(fetchQueue, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchQueue = async () => {
    try {
      const res = await api.get("/admin/queue");
      setQueue(res.data.queue || []);
    } catch (err: any) {
      if (err.response?.status === 401) {
        handleLogout();
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    router.push("/");
  };

  const handleFileUpload = async (file: File, type: "ad" | "debate") => {
    if (!file.name.endsWith(".mp4")) {
      alert("Only .mp4 files are allowed for broadcast.");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("type", type);
    formData.append("title", file.name);

    try {
      await api.post("/admin/upload-media", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      fetchQueue();
    } catch (err) {
      console.error(err);
      alert("Failed to upload media. Check server logs.");
    } finally {
      setUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      // Default to ad on raw drag-drop, they can selectively upload using buttons
      handleFileUpload(e.dataTransfer.files[0], "ad");
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-white">
      {/* Top Navbar */}
      <nav className="bg-black/40 border-b border-white/10 px-6 py-4 flex justify-between items-center backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(220,38,38,0.5)]">
            <Video size={18} className="text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">VartaPravah Master Control</h1>
        </div>
        <div className="flex items-center space-x-6">
          <div className="flex flex-col text-right">
            <span className="text-xs text-gray-400 font-mono">LIVE SERVER</span>
            <span className="text-sm font-semibold text-green-400 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              ONLINE
            </span>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors bg-white/5 hover:bg-red-500/20 px-4 py-2 rounded-lg"
          >
            <LogOut size={16} />
            <span className="text-sm font-medium">Disconnect</span>
          </button>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
        
        {/* Left Column: Upload Zone */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-2xl">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <UploadCloud size={20} className="text-blue-400" />
              Priority Media Injection
            </h2>
            <p className="text-gray-400 text-sm mb-6">
              Upload MP4 files here. They will be placed at the <b>absolute front</b> of the YouTube RTMP stream queue and will play locally after the current clip finishes.
            </p>

            <div 
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={onDrop}
              className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${isDragging ? 'border-red-500 bg-red-500/10' : 'border-white/20 hover:border-white/40 bg-black/20'}`}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept="video/mp4"
                aria-label="Upload Video"
                title="Upload Video"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileUpload(e.target.files[0], "ad");
                  }
                }}
              />
              <UploadCloud size={48} className={`mx-auto mb-4 ${isDragging ? 'text-red-400' : 'text-gray-500'}`} />
              <h3 className="text-xl font-medium mb-2">Drag & Drop MP4 Video</h3>
              <p className="text-gray-500 text-sm mb-6">or use the categorized buttons below</p>
              
              <div className="flex justify-center gap-4">
                <button 
                  disabled={uploading}
                  onClick={() => {
                    if (fileInputRef.current) {
                      fileInputRef.current.onchange = (e: any) => {
                        if (e.target.files[0]) handleFileUpload(e.target.files[0], "ad");
                      };
                      fileInputRef.current.click();
                    }
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-lg shadow-blue-900/20 disabled:opacity-50"
                >
                  {uploading ? 'Injecting...' : 'Inject Video Ad'}
                </button>
                <button 
                  disabled={uploading}
                  onClick={() => {
                    if (fileInputRef.current) {
                      fileInputRef.current.onchange = (e: any) => {
                        if (e.target.files[0]) handleFileUpload(e.target.files[0], "debate");
                      };
                      fileInputRef.current.click();
                    }
                  }}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-lg shadow-purple-900/20 disabled:opacity-50"
                >
                  {uploading ? 'Injecting...' : 'Inject Live Debate'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Active Queue */}
        <div className="space-y-6">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-2xl h-full">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <PlaySquare size={20} className="text-green-400" />
                Priority Queue
              </h2>
              <span className="bg-white/10 text-xs px-2.5 py-1 rounded-full font-mono">{queue.length} items</span>
            </div>

            {queue.length === 0 ? (
              <div className="text-center py-12 text-gray-500 border border-dashed border-white/10 rounded-xl bg-black/20">
                <AlertCircle size={32} className="mx-auto mb-3 opacity-50" />
                <p className="text-sm">Queue empty.</p>
                <p className="text-xs mt-1">Stream engine is safely pulling auto-generated AI news.</p>
              </div>
            ) : (
              <ul className="space-y-3">
                {queue.map((item: any, idx: number) => (
                  <li key={idx} className="bg-black/40 border border-white/5 rounded-lg p-4 flex items-center animate-in fade-in slide-in-from-bottom-4">
                    <div className="mr-4 text-gray-500 font-mono text-sm font-bold">
                      {idx + 1}.
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate text-white" title={item.title}>
                        {item.title}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-sm ${item.type === 'ad' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'}`}>
                          {item.type}
                        </span>
                        <span className="text-[10px] text-gray-500 font-mono">
                          {new Date(item.added_at * 1000).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
            
            {queue.length > 0 && (
              <div className="mt-6 text-xs text-gray-400 bg-red-500/10 border border-red-500/20 p-3 rounded-lg">
                <span className="font-bold text-red-400 uppercase tracking-wider block mb-1">Live Interruption Warning</span>
                The stream engine will play the #1 item in this queue immediately after the current video finishes.
              </div>
            )}
          </div>
        </div>

      </main>
    </div>
  );
}
