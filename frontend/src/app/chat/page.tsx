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
        <div className="flex flex-col p-6" style={{ height: '100vh' }}>
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h1 className="text-3xl font-bold">RAG Assistant</h1>
                    <p className="text-muted-foreground mt-1">Grounded knowledge from maintenance manuals and operating procedures</p>
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
                className="flex-1 overflow-y-auto mb-4 flex flex-col gap-4 p-6 rounded-xl bg-card/30 border"
            >
                {messages.map((m, i) => (
                    <div key={i} className={`flex items-start gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg mt-1 ${m.role === 'user' ? 'bg-primary' : 'bg-secondary'}`}>
                            {m.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                        </div>
                        <div className={`flex flex-col gap-2 max-w-[75%] ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                            <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${m.role === 'user' ? 'bg-primary/20 rounded-tr-sm' : 'bg-secondary rounded-tl-sm'}`}>
                                {m.text}
                            </div>
                            {m.citations && m.citations.length > 0 && (
                                <div className="flex flex-col gap-2 w-full mt-1">
                                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider px-1">Sources</p>
                                    {m.citations.map((c, j) => (
                                        <CitationCard key={j} citation={c} />
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-secondary mt-1">
                            <Loader2 size={16} className="animate-spin" />
                        </div>
                        <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-secondary text-sm italic text-muted-foreground">
                            Thinking...
                        </div>
                    </div>
                )}
            </div>

            <form onSubmit={handleSend} className="flex gap-3">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about maintenance, oil levels, solar cleaning..."
                    className="flex-1 bg-card border p-4 rounded-xl focus:outline-none focus:border-primary transition-colors text-sm"
                    disabled={loading}
                />
                <button
                    type="submit"
                    className="bg-primary p-4 px-6 rounded-xl hover:brightness-110 transition-all disabled:opacity-50"
                    disabled={loading}
                >
                    <Send size={18} />
                </button>
            </form>
        </div>
    );
}
