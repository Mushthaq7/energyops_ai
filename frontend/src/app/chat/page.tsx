"use client";

import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Loader2, BookOpen } from "lucide-react";
import { ragApi } from "@/lib/api";
import CitationCard from "@/components/CitationCard";

interface Message {
    role: "user" | "assistant";
    text: string;
    citations?: any[];
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        { role: "assistant", text: "Hello! I'm your EnergyOps Assistant. How can I help you with plant maintenance or operations today?" }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userText = input;
        setInput("");
        setMessages(prev => [...prev, { role: "user", text: userText }]);
        setLoading(true);

        try {
            const data = await ragApi.ask(userText);
            setMessages(prev => [...prev, {
                role: "assistant",
                text: data.answer,
                citations: data.citations
            }]);
        } catch (err) {
            setMessages(prev => [...prev, {
                role: "assistant",
                text: "I'm sorry, I encountered an error while processing your request."
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col" style={{ height: 'calc(100vh - 4rem)', padding: '1rem' }}>
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">RAG Assistant</h1>
                    <p className="text-muted">Grounded knowledge from maintenance manuals and operating procedures</p>
                </div>
                <button
                    onClick={() => ragApi.index()}
                    className="flex items-center gap-2 p-2 px-4 border rounded-lg hover:bg-secondary transition-colors text-sm"
                >
                    <BookOpen size={16} />
                    <span>Re-index Docs</span>
                </button>
            </div>

            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto mb-4 flex flex-col gap-6 p-4 rounded-xl bg-card/30 border glass"
            >
                {messages.map((m, i) => (
                    <div key={i} className={`flex gap-4 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`p-2 rounded-lg h-fit ${m.role === 'user' ? 'bg-primary' : 'bg-secondary'}`}>
                            {m.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                        </div>
                        <div className={`flex flex-col gap-3 max-w-[80%] ${m.role === 'user' ? 'items-end' : ''}`}>
                            <div className={`p-4 rounded-2xl ${m.role === 'user' ? 'bg-primary/20 rounded-tr-none' : 'bg-secondary rounded-tl-none'}`}>
                                <p className="leading-relaxed">{m.text}</p>
                            </div>

                            {m.citations && m.citations.length > 0 && (
                                <div className="grid grid-cols-1 gap-3 mt-2">
                                    <p className="text-xs font-bold text-muted uppercase tracking-wider">Citations:</p>
                                    {m.citations.map((c, j) => (
                                        <CitationCard key={j} citation={c} />
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-4">
                        <div className="p-2 rounded-lg bg-secondary">
                            <Loader2 size={20} className="animate-spin" />
                        </div>
                        <div className="p-4 rounded-2xl bg-secondary rounded-tl-none italic text-muted">Thinking...</div>
                    </div>
                )}
            </div>

            <form onSubmit={handleSend} className="flex gap-3">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about maintenance, oil levels, solar cleaning..."
                    className="flex-1 bg-card border p-4 rounded-xl focus:outline-none focus:border-primary transition-colors"
                    disabled={loading}
                />
                <button
                    type="submit"
                    className="bg-primary p-4 px-8 rounded-xl font-bold hover:brightness-110 transition-all disabled:opacity-50"
                    disabled={loading}
                >
                    <Send size={20} />
                </button>
            </form>
        </div>
    );
}
