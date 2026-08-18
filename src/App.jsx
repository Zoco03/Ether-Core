import React, { useState, useRef, useEffect } from 'react';
import { 
  Paperclip, Mic, Send, Bot, Code, MessageSquare, 
  Search, ChevronDown, Plus, Trash2, AtSign, X, Terminal
} from 'lucide-react';

export default function App() {
  // Chat History Management
  const [chats, setChats] = useState([
    { id: 'chat-1', title: 'Marketing Analytics Suite', messages: [] }
  ]);
  const [currentChatId, setCurrentChatId] = useState('chat-1');

  const [input, setInput] = useState('');
  const [mode, setMode] = useState('2'); // Default to Code Mode
  const [asyncExecution, setAsyncExecution] = useState(false);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showTagMenu, setShowTagMenu] = useState(false);

  // Dynamic Multi-Agent Specialists State
  const [specialists, setSpecialists] = useState([]);

  // Inline @ Mention Popover State
  const [mentionMenu, setMentionMenu] = useState({ visible: false, filterText: '', matchIndex: -1 });
  const [selectedIndex, setSelectedIndex] = useState(0);

  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const activeChat = chats.find(c => c.id === currentChatId) || chats[0];

  // Fetch dynamic agents live from backend with Array validation guard
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/agents')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setSpecialists(data);
        } else {
          throw new Error("API response is not an array");
        }
      })
      .catch(() => {
        // Fallback initial list
        setSpecialists([
          { tag: '@frontend_sp1', name: 'Frontend Sp1', icon: '🎨' },
          { tag: '@frontend_sp2', name: 'Frontend Sp2', icon: '📊' },
          { tag: '@backend_sp1', name: 'Backend Sp1', icon: '⚙️' },
          { tag: '@backend_sp2', name: 'Backend Sp2', icon: '🗄️' },
          { tag: '@research_sp', name: 'Research Sp', icon: '🔬' }
        ]);
      });
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeChat?.messages, loading]);

  // Handle Dynamic @ Mention Popup Triggering
  const handleInputChange = (e) => {
    const value = e.target.value;
    const cursorPos = e.target.selectionStart;
    setInput(value);

    const textBeforeCursor = value.slice(0, cursorPos);
    const lastAtPos = textBeforeCursor.lastIndexOf('@');

    if (lastAtPos !== -1) {
      const charBeforeAt = lastAtPos > 0 ? textBeforeCursor[lastAtPos - 1] : ' ';
      const query = textBeforeCursor.slice(lastAtPos + 1);

      if ((/[\s\n]|^/).test(charBeforeAt) && !/\s/.test(query)) {
        setMentionMenu({ visible: true, filterText: query.toLowerCase(), matchIndex: lastAtPos });
        setSelectedIndex(0);
        return;
      }
    }

    setMentionMenu({ visible: false, filterText: '', matchIndex: -1 });
  };

  // Safe filter calculation ensuring Array type
  const filteredSpecialists = Array.isArray(specialists)
    ? specialists.filter(sp => 
        sp.tag?.toLowerCase().includes(mentionMenu.filterText) || 
        sp.name?.toLowerCase().includes(mentionMenu.filterText)
      )
    : [];

  const selectMention = (agent) => {
    if (mentionMenu.matchIndex === -1) return;

    const beforeAt = input.slice(0, mentionMenu.matchIndex);
    const cursorPos = textareaRef.current ? textareaRef.current.selectionStart : input.length;
    const afterCursor = input.slice(cursorPos);

    const newInput = `${beforeAt}${agent.tag} ${afterCursor}`;
    setInput(newInput);
    setMentionMenu({ visible: false, filterText: '', matchIndex: -1 });

    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (mentionMenu.visible && filteredSpecialists.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredSpecialists.length);
        return;
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredSpecialists.length) % filteredSpecialists.length);
        return;
      } else if (e.key === 'Enter' || e.key === 'Tab') {
        e.preventDefault();
        selectMention(filteredSpecialists[selectedIndex]);
        return;
      } else if (e.key === 'Escape') {
        setMentionMenu({ visible: false, filterText: '', matchIndex: -1 });
        return;
      }
    }

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleNewChat = () => {
    const newId = `chat-${Date.now()}`;
    const newChat = { id: newId, title: 'New Multi-Agent Thread', messages: [] };
    setChats([newChat, ...chats]);
    setCurrentChatId(newId);
  };

  const handleDeleteChat = (id, e) => {
    e.stopPropagation();
    if (chats.length === 1) return;
    const filtered = chats.filter(c => c.id !== id);
    setChats(filtered);
    if (currentChatId === id) {
      setCurrentChatId(filtered[0].id);
    }
  };

  const insertTag = (tag) => {
    setInput(prev => prev ? `${prev} ${tag} ` : `${tag} `);
    setShowTagMenu(false);
  };

  const handleFileUpload = (e) => {
    const uploaded = Array.from(e.target.files);
    if (files.length + uploaded.length > 5) {
      alert("Maximum 5 attachments allowed.");
      return;
    }
    setFiles(prev => [...prev, ...uploaded]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    setIsRecording(true);
    recognition.start();

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      setInput(prev => prev ? `${prev} ${transcript}` : transcript);
      setIsRecording(false);
    };
    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if ((!input.trim() && files.length === 0) || loading) return;

    let fileContext = "";
    for (const f of files) {
      const txt = await f.text();
      fileContext += `\n\n--- FILE: ${f.name} ---\n${txt}\n--- END FILE ---`;
    }

    const promptWithContext = `${input}${fileContext}`;
    const userMsg = { role: 'user', content: input, files: files.map(f => f.name) };

    setChats(prev => prev.map(c => {
      if (c.id === currentChatId) {
        const title = c.messages.length === 0 ? input.slice(0, 30) + '...' : c.title;
        return { ...c, title, messages: [...c.messages, userMsg] };
      }
      return c;
    }));

    setInput('');
    setFiles([]);
    setLoading(true);
    setMentionMenu({ visible: false, filterText: '', matchIndex: -1 });

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptWithContext, mode: mode, async_execution: asyncExecution })
      });

      const data = await res.json();

      const botMsg = { 
        role: 'assistant', 
        content: data.response?.trim() ? data.response : '⚠️ Response empty. Check backend terminal logs.', 
        savedFiles: data.saved_files 
      };

      setChats(prev => prev.map(c => {
        if (c.id === currentChatId) {
          return { ...c, messages: [...c.messages, botMsg] };
        }
        return c;
      }));

    } catch (err) {
      setChats(prev => prev.map(c => {
        if (c.id === currentChatId) {
          return { ...c, messages: [...c.messages, { role: 'assistant', content: '❌ Failed to connect to Ether Core backend.' }] };
        }
        return c;
      }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0A0A0A] text-gray-200 font-sans overflow-hidden">
      
      {/* LEFT SIDEBAR: CHAT HISTORY */}
      <aside className="w-72 bg-[#121212] border-r border-gray-800/80 flex flex-col justify-between p-4 shrink-0">
        <div>
          <div className="flex items-center justify-between mb-6 px-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#00FFFF] shadow-[0_0_10px_#00FFFF]" />
              <h1 className="text-lg font-bold text-white tracking-wider">Ether Core</h1>
            </div>
            <button 
              onClick={handleNewChat}
              className="p-1.5 bg-[#1A1A1A] hover:bg-[#00FFFF]/20 text-[#00FFFF] border border-[#00FFFF]/30 rounded-lg transition"
              title="New Chat"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <div className="text-xs uppercase font-semibold text-gray-500 mb-2 px-2">Chat History</div>
          <div className="space-y-1.5 overflow-y-auto max-h-[calc(100vh-180px)] pr-1">
            {chats.map(c => (
              <div
                key={c.id}
                onClick={() => setCurrentChatId(c.id)}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer text-xs transition-all ${
                  currentChatId === c.id 
                    ? 'bg-[#00FFFF]/10 text-[#00FFFF] border border-[#00FFFF]/30 font-medium' 
                    : 'text-gray-400 hover:bg-gray-800/40 hover:text-gray-200'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <MessageSquare className="w-3.5 h-3.5 shrink-0" />
                  <span className="truncate">{c.title}</span>
                </div>
                {chats.length > 1 && (
                  <Trash2 
                    className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition" 
                    onClick={(e) => handleDeleteChat(c.id, e)}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="text-[11px] text-gray-600 px-2 pt-3 border-t border-gray-800/50">
          Parallel Agent Engine v2026
        </div>
      </aside>

      {/* MAIN CANVAS */}
      <main className="flex-1 flex flex-col justify-between relative bg-[#0A0A0A]">
        
        {/* Messages Window */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 max-w-4xl mx-auto w-full">
          {activeChat.messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center pt-28">
              <div className="relative mb-6">
                <div className="w-16 h-16 rounded-full border-2 border-[#00FFFF]/30 flex items-center justify-center bg-[#00FFFF]/5">
                  <Terminal className="w-8 h-8 text-[#00FFFF]" />
                </div>
                <div className="absolute -inset-1 rounded-full border border-[#00FFFF]/20 animate-ping" />
              </div>
              <h2 className="text-3xl font-light text-white mb-2">Parallel Agent Workspace</h2>
              <p className="text-gray-500 text-sm max-w-lg leading-relaxed">
                Tag specialists directly in your prompt (<span className="text-[#00FFFF]">@frontend_sp1</span>, <span className="text-[#00FFFF]">@backend_sp2</span>). Doxi Boss Agent aligns master context and coordinates execution.
              </p>
            </div>
          ) : (
            activeChat.messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-[#00FFFF]/10 border border-[#00FFFF]/30 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 text-[#00FFFF]" />
                  </div>
                )}

                <div className={`max-w-2xl rounded-2xl px-5 py-3.5 ${
                  msg.role === 'user' 
                    ? 'bg-[#181818] text-white border border-gray-800' 
                    : 'bg-[#121212] text-gray-200 border border-gray-800/80 shadow-xl'
                }`}>
                  {msg.files?.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-2">
                      {msg.files.map((f, i) => (
                        <span key={i} className="text-xs bg-[#00FFFF]/10 text-[#00FFFF] px-2 py-0.5 rounded border border-[#00FFFF]/20">
                          📎 {f}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="whitespace-pre-wrap leading-relaxed text-sm font-mono">
                    {msg.content}
                  </div>

                  {msg.savedFiles?.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-800 text-xs text-[#00FFFF]">
                      ✅ Auto-saved generated files: {msg.savedFiles.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {/* CYBER-RADAR LOADING ANIMATION */}
          {loading && (
            <div className="flex items-center gap-4 bg-[#121212] border border-[#00FFFF]/30 rounded-2xl p-5 max-w-md shadow-[0_0_20px_rgba(0,255,255,0.08)]">
              <div className="relative w-10 h-10 shrink-0 flex items-center justify-center">
                <div className="absolute inset-0 rounded-full border-2 border-t-[#00FFFF] border-r-transparent border-b-[#00FFFF]/30 border-l-transparent animate-spin" />
                <div className="absolute inset-1.5 rounded-full border border-dashed border-[#00FFFF]/40 animate-spin [animation-duration:3s]" />
                <div className="w-2 h-2 rounded-full bg-[#00FFFF] shadow-[0_0_8px_#00FFFF]" />
              </div>

              <div>
                <div className="text-xs font-semibold text-[#00FFFF] tracking-wider uppercase">
                  Doxi Boss Agent Active
                </div>
                <div className="text-xs text-gray-400 mt-0.5">
                  Synchronizing specialists & executing tasks...
                </div>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* FLOATING INPUT DOCK */}
        <div className="p-4 max-w-4xl mx-auto w-full relative">
          
          {/* @ MENTION POPUP MENU */}
          {mentionMenu.visible && filteredSpecialists.length > 0 && (
            <div className="absolute bottom-full mb-3 left-4 right-4 md:left-0 md:right-0 bg-[#161616] border border-[#00FFFF]/30 rounded-2xl shadow-[0_0_25px_rgba(0,0,0,0.8)] overflow-hidden z-50 max-h-56 overflow-y-auto">
              <div className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-gray-500 border-b border-gray-800 bg-[#121212]">
                Select Specialist Agent
              </div>
              {filteredSpecialists.map((sp, idx) => (
                <div
                  key={sp.tag || idx}
                  onClick={() => selectMention(sp)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-4 py-2.5 cursor-pointer text-xs transition-colors ${
                    idx === selectedIndex 
                      ? 'bg-[#00FFFF]/15 text-[#00FFFF]' 
                      : 'text-gray-300 hover:bg-gray-800/40'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-base">{sp.icon}</span>
                    <span className="font-mono font-semibold">{sp.tag}</span>
                  </div>
                  <span className="text-[11px] text-gray-400 font-sans">{sp.name}</span>
                </div>
              ))}
            </div>
          )}

          {files.length > 0 && (
            <div className="flex gap-2 mb-2 overflow-x-auto p-2 bg-[#121212] rounded-xl border border-gray-800">
              {files.map((f, i) => (
                <span key={i} className="text-xs bg-[#00FFFF]/10 text-[#00FFFF] px-2.5 py-1 rounded-full flex items-center gap-1.5 border border-[#00FFFF]/30">
                  {f.name}
                  <X className="w-3 h-3 cursor-pointer hover:text-white" onClick={() => removeFile(i)} />
                </span>
              ))}
            </div>
          )}

          {/* Dynamic Specialist Tag Picker Bar */}
          {showTagMenu && (
            <div className="flex flex-wrap gap-1.5 p-2 mb-2 bg-[#141414] border border-[#00FFFF]/30 rounded-xl">
              {Array.isArray(specialists) && specialists.map((sp, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => insertTag(sp.tag)}
                  className="text-xs bg-[#1A1A1A] hover:bg-[#00FFFF]/20 text-[#00FFFF] px-2.5 py-1 rounded-lg border border-gray-800 transition flex items-center gap-1"
                >
                  <span>{sp.icon}</span> {sp.tag}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={handleSubmit} className="bg-[#141414] border border-gray-800 focus-within:border-[#00FFFF]/50 rounded-2xl p-3 shadow-2xl transition-all">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="e.g. @frontend_sp1 build landing page, @backend_sp2 setup DB..."
              className="w-full bg-transparent text-gray-100 placeholder-gray-500 text-sm focus:outline-none resize-none px-2 max-h-32 min-h-[44px]"
            />

            <div className="flex items-center justify-between pt-2 border-t border-gray-800/60 mt-1">
              
              <div className="flex items-center gap-2">
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileUpload} 
                  multiple 
                  className="hidden" 
                />
                
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-gray-400 hover:text-[#00FFFF] hover:bg-gray-800/50 rounded-lg transition"
                  title="Attach Files"
                >
                  <Paperclip className="w-4 h-4" />
                </button>

                <button
                  type="button"
                  onClick={() => setShowTagMenu(!showTagMenu)}
                  className="p-2 text-gray-400 hover:text-[#00FFFF] hover:bg-gray-800/50 rounded-lg transition flex items-center gap-1 text-xs"
                  title="Insert Agent Tag"
                >
                  <AtSign className="w-4 h-4 text-[#00FFFF]" />
                </button>

                <div className="relative inline-block text-xs">
                  <select
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                    className="bg-[#1A1A1A] text-[#00FFFF] border border-[#00FFFF]/30 rounded-lg px-2.5 py-1.5 focus:outline-none cursor-pointer pr-6 appearance-none"
                  >
                    <option value="1">Mode: Answer</option>
                    <option value="2">Mode: Code</option>
                    <option value="3">Mode: Research</option>
                  </select>
                  <ChevronDown className="w-3 h-3 text-[#00FFFF] absolute right-2 top-2.5 pointer-events-none" />
                </div>

                {/* NEW ASYNC TOGGLE */}
                <button
                  type="button"
                  onClick={() => setAsyncExecution(!asyncExecution)}
                  className={`px-2.5 py-1.5 rounded-lg border text-xs font-medium transition ${
                    asyncExecution 
                      ? 'bg-[#00FFFF]/20 border-[#00FFFF]/50 text-[#00FFFF]' 
                      : 'bg-[#1A1A1A] border-gray-800 text-gray-400 hover:text-gray-300'
                  }`}
                  title="Toggle Async Execution"
                >
                  ⚡ Async {asyncExecution ? 'ON' : 'OFF'}
                </button>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleVoiceInput}
                  className={`p-2 rounded-lg transition ${
                    isRecording 
                      ? 'bg-red-500/20 text-red-400 border border-red-500/50 animate-pulse' 
                      : 'text-gray-400 hover:text-[#00FFFF] hover:bg-gray-800/50'
                  }`}
                  title="Voice Command"
                >
                  <Mic className="w-4 h-4" />
                </button>

                <button
                  type="submit"
                  disabled={loading || (!input.trim() && files.length === 0)}
                  className="p-2 bg-[#00FFFF] text-black rounded-lg hover:bg-[#33FFFF] disabled:opacity-30 disabled:hover:bg-[#00FFFF] transition font-medium"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>

            </div>
          </form>
        </div>
      </main>
    </div>
  );
}