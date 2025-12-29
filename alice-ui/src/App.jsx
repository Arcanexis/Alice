import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Bot, User, ChevronDown, ChevronUp, ScrollText, Library, Terminal, FileText, Download, ExternalLink, Code2, AlertCircle, CheckCircle2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// 自定义代码块组件，实现折叠功能 (始终保持深色)
const CodeBlock = ({ children, className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const lang = className ? className.replace('language-', '') : 'code';
  
  return (
    <details className="my-2 border border-gray-800 rounded-lg overflow-hidden bg-gray-900/50 shadow-sm transition-all" open={isOpen} onToggle={(e) => setIsOpen(e.target.open)}>
      <summary className="px-3 py-1.5 text-xs text-gray-400 cursor-pointer hover:bg-gray-800 flex items-center justify-between select-none font-mono">
        <div className="flex items-center gap-2">
          <Code2 size={12} className="text-indigo-400" />
          <span>{lang.toUpperCase()} 脚本 / 资源块</span>
        </div>
        <div className="flex items-center gap-2">
            <span className="text-[10px] bg-gray-800 px-1.5 rounded text-gray-400 uppercase">{isOpen ? '收起' : '展开内容'}</span>
            {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </summary>
      <div className="border-t border-gray-800">
        <pre className="p-3 overflow-x-auto bg-black/40 text-white text-xs leading-relaxed">
          <code className={className}>{children}</code>
        </pre>
      </div>
    </details>
  );
};

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [tasks, setTasks] = useState('');
  const [skills, setSkills] = useState({});
  const [outputs, setOutputs] = useState([]);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchStatus();
    const timer = setInterval(fetchStatus, 5000); // 每 5 秒轮询一次状态
    return () => clearInterval(timer);
  }, []);

  const fetchStatus = async () => {
    try {
      const [taskRes, skillRes, outputRes] = await Promise.all([
        axios.get('/api/tasks'),
        axios.get('/api/skills'),
        axios.get('/api/outputs')
      ]);
      setTasks(taskRes.data.content);
      setSkills(skillRes.data.skills);
      setOutputs(outputRes.data.files);
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    let currentBotMessage = { role: 'bot', thinking: '', content: '', executionResults: [] };
    setMessages((prev) => [...prev, currentBotMessage]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            if (data.type === 'thinking') {
              currentBotMessage.thinking += data.delta;
            } else if (data.type === 'content') {
              currentBotMessage.content += data.delta;
            } else if (data.type === 'execution_result') {
                currentBotMessage.executionResults.push(data.content);
            }

            setMessages((prev) => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1] = { ...currentBotMessage };
              return newMessages;
            });
          } catch (e) {
            console.error('Error parsing chunk:', e, line);
          }
        }
      }
    } catch (err) {
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
      fetchStatus();
    }
  };

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100 overflow-hidden font-sans selection:bg-indigo-500/30">
      {/* Sidebar */}
      <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col hidden lg:flex shadow-2xl z-10">
        <div className="p-6 border-b border-gray-800 flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-900/20">
            <Bot className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-100 leading-none">Alice Agent</h1>
            <span className="text-[10px] text-indigo-400 font-medium uppercase tracking-wider">Experimental Lab</span>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-8 scrollbar-thin scrollbar-thumb-gray-800">
          <section>
            <div className="flex items-center gap-2 mb-3 text-gray-100 font-bold px-2 text-sm uppercase tracking-wider">
              <ScrollText size={16} className="text-indigo-400" />
              <span>任务清单 (Todo)</span>
            </div>
            <div className="bg-indigo-900/10 rounded-xl p-4 text-sm text-gray-300 whitespace-pre-wrap border border-indigo-900/20 max-h-48 overflow-y-auto">
              {tasks || '暂无活跃任务'}
            </div>
          </section>

          <section>
            <div className="flex items-center gap-2 mb-3 text-gray-100 font-bold px-2 text-sm uppercase tracking-wider">
              <FileText size={16} className="text-indigo-400" />
              <span>成果物 (Outputs)</span>
            </div>
            <div className="space-y-1 px-1">
              {outputs.length > 0 ? (
                outputs.map(file => (
                  <div key={file.name} className="flex items-center justify-between p-2.5 hover:bg-gray-800 rounded-xl group transition-colors">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center text-gray-500 group-hover:bg-indigo-900/30 group-hover:text-indigo-400 transition-colors shrink-0">
                        <FileText size={16} />
                      </div>
                      <a href={file.url} target="_blank" rel="noreferrer" className="flex flex-col overflow-hidden hover:opacity-80 transition-opacity">
                        <span className="text-xs text-gray-200 truncate font-semibold">{file.name}</span>
                        <span className="text-[10px] text-gray-500">{(file.size / 1024).toFixed(1)} KB</span>
                      </a>
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <a href={file.url} target="_blank" rel="noreferrer" className="p-1.5 text-gray-500 hover:text-indigo-400 hover:bg-gray-700 rounded-md shadow-sm border border-transparent" title="预览">
                        <ExternalLink size={14} />
                      </a>
                      <a href={file.url} download className="p-1.5 text-gray-500 hover:text-indigo-400 hover:bg-gray-700 rounded-md shadow-sm border border-transparent" title="下载">
                        <Download size={14} />
                      </a>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-gray-500 text-center py-4 italic bg-gray-800/50 rounded-xl border border-dashed border-gray-700">
                  尚未生成任何文件
                </div>
              )}
            </div>
          </section>

          <section>
            <div className="flex items-center gap-2 mb-3 text-gray-100 font-bold px-2 text-sm uppercase tracking-wider">
              <Library size={16} className="text-indigo-400" />
              <span>技能库 (Skills)</span>
            </div>
            <div className="grid grid-cols-1 gap-2 px-1">
              {Object.keys(skills).map(name => (
                <div key={name} className="p-3 bg-gray-800/50 border border-gray-800 rounded-xl shadow-sm hover:shadow-md transition-shadow group">
                  <div className="font-bold text-gray-200 text-xs mb-1 group-hover:text-indigo-400 transition-colors">{name}</div>
                  <div className="text-[10px] text-gray-500 line-clamp-2 leading-relaxed">{skills[name].description}</div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative z-0">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth bg-gray-950">
          {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-gray-600 space-y-4">
                  <Bot size={48} className="text-gray-800" />
                  <p className="text-sm font-medium">今天有什么我可以帮你的吗？</p>
              </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={cn("flex w-full animate-in fade-in slide-in-from-bottom-2 duration-300", msg.role === 'user' ? "justify-end" : "justify-start")}>
              <div className={cn("max-w-[85%] flex gap-4", msg.role === 'user' ? "flex-row-reverse" : "flex-row")}>
                <div className={cn(
                  "w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 shadow-md",
                  msg.role === 'user' ? "bg-gray-800 text-indigo-400 border border-indigo-900/50" : "bg-indigo-600 text-white"
                )}>
                  {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                
                <div className="space-y-3">
                  {msg.role === 'bot' && msg.thinking && (
                    <details className="group bg-gray-900/80 backdrop-blur-sm rounded-xl border border-gray-800 overflow-hidden transition-all">
                      <summary className="px-3 py-1.5 text-[11px] text-gray-400 cursor-pointer hover:bg-gray-800 flex items-center justify-between select-none">
                        <div className="flex items-center gap-2">
                          <Terminal size={12} className="animate-pulse text-indigo-400" />
                          <span className="font-semibold uppercase tracking-tight">思考过程 (Reasoning)</span>
                        </div>
                        <ChevronDown size={14} className="group-open:rotate-180 transition-transform" />
                      </summary>
                      <div className="px-4 py-3 text-xs text-gray-400 italic border-t border-gray-800 bg-black/20 whitespace-pre-wrap font-mono leading-relaxed">
                        {msg.thinking}
                      </div>
                    </details>
                  )}

                  <div className={cn(
                    "rounded-2xl px-5 py-3 shadow-sm leading-relaxed",
                    msg.role === 'user' ? "bg-gray-800 text-gray-100 border border-gray-700" : "bg-gray-900 text-gray-200 border border-gray-800"
                  )}>
                    <ReactMarkdown 
                      className="prose prose-sm max-w-none prose-invert prose-headings:font-bold prose-a:text-indigo-400 prose-pre:p-0 prose-pre:bg-transparent prose-pre:m-0"
                      components={{
                        code: ({ node, inline, className, children, ...props }) => {
                          return inline ? (
                            <code className={cn("bg-gray-800 text-pink-400 px-1.5 py-0.5 rounded font-mono text-[0.85em] font-medium", className)} {...props}>
                              {children}
                            </code>
                          ) : (
                            <CodeBlock className={className}>{children}</CodeBlock>
                          );
                        }
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>

                  {msg.role === 'bot' && msg.executionResults && msg.executionResults.length > 0 && (
                    <details className="group bg-black rounded-xl overflow-hidden mt-3 shadow-none border border-gray-800">
                      <summary className="px-3 py-2 text-[11px] text-gray-400 cursor-pointer hover:bg-gray-900 flex items-center justify-between select-none font-mono">
                        <div className="flex items-center gap-2">
                          <Terminal size={12} />
                          <span>沙盒执行反馈 ({msg.executionResults.length})</span>
                          <span className="flex items-center gap-1 ml-2 text-[9px] px-1.5 rounded bg-gray-900 border border-gray-800">
                            {msg.executionResults.some(r => r.includes('执行失败')) ? 
                                <><AlertCircle size={10} className="text-red-500" /> <span className="text-red-400">异常终止</span></> : 
                                <><CheckCircle2 size={10} className="text-green-500" /> <span className="text-green-400">流水线就绪</span></>
                            }
                          </span>
                        </div>
                        <ChevronDown size={14} className="group-open:rotate-180 transition-transform" />
                      </summary>
                      <div className="space-y-3 p-3 border-t border-gray-800 max-h-80 overflow-y-auto bg-black/40">
                        {msg.executionResults.map((res, idx) => (
                          <div key={idx} className="text-[10px] text-green-400 font-mono overflow-x-auto whitespace-pre-wrap pb-3 border-b border-gray-800 last:border-0 last:pb-0">
                            <div className="text-gray-500 mb-1 flex justify-between">
                                <span># LOG_BLOCK_{idx + 1}</span>
                                <span className={res.includes('执行失败') ? "text-red-500" : "text-gray-600"}>
                                    {res.includes('执行失败') ? "[ERR_STATUS]" : "[OK_STATUS]"}
                                </span>
                            </div>
                            {res}
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 bg-gray-950/80 backdrop-blur-md border-t border-gray-800">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isLoading ? "Alice 正在全神贯注思考中..." : "问问 Alice，或要求她执行任务..."}
              disabled={isLoading}
              className="w-full pl-5 pr-14 py-4 bg-gray-900 border border-gray-800 rounded-2xl focus:outline-none focus:ring-4 focus:ring-indigo-500/5 focus:border-indigo-500 focus:bg-gray-900 transition-all disabled:bg-gray-950 disabled:text-gray-600 text-gray-100 shadow-inner"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2.5 top-2.5 bg-indigo-600 text-white p-2.5 rounded-xl hover:bg-indigo-700 transition-all disabled:bg-gray-800 shadow-none active:scale-95"
            >
              <Send size={20} />
            </button>
          </form>
          <div className="flex justify-center gap-6 mt-4 opacity-50">
              <div className="flex items-center gap-1.5 text-[10px] text-gray-600">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                  容器沙盒已挂载
              </div>
              <div className="flex items-center gap-1.5 text-[10px] text-gray-600 border-l border-gray-800 pl-6">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
                  分级记忆库同步中
              </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
