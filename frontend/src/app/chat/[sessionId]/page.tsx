'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import api from '@/lib/api';
import Link from 'next/link';
import Skeleton from '@/components/Skeleton';

interface Message {
    id: number;
    role: string;
    content: string;
    sql_query?: string;
    created_at: string;
}

export default function ChatSessionPage() {
    const params = useParams();
    const sessionId = params.sessionId;
    const [messages, setMessages] = useState<Message[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (!sessionId) return;
        const fetchSession = async () => {
            try {
                const response = await api.get(`/chat/sessions/${sessionId}`);
                setMessages(response.data.messages);
            } catch (error) {
                console.error('Failed to fetch session', error);
            }
        };
        fetchSession();
    }, [sessionId]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        const tempMsg = { id: Date.now(), role: 'user', content: newMessage, created_at: new Date().toISOString() };
        setMessages((prev) => [...prev, tempMsg]);
        setNewMessage('');
        setLoading(true);

        try {
            const response = await api.post(`/chat/sessions/${sessionId}/messages`, {
                message: tempMsg.content,
                connection_id: 0 // Ignored by backend for existing session
            });
            setMessages((prev) => [...prev, response.data]);
        } catch (error) {
            console.error('Failed to send message', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow p-4 flex items-center">
                <Link href="/chat" className="text-gray-500 hover:text-gray-700 mr-4">
                    ← Back
                </Link>
                <h1 className="text-xl font-bold">Chat Session</h1>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-3xl rounded-lg p-4 ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white shadow text-gray-900'}`}>
                            <p className="whitespace-pre-wrap">{msg.content}</p>
                            {msg.sql_query && (
                                <div className="mt-2 p-2 bg-gray-100 rounded text-xs font-mono text-gray-700 overflow-x-auto">
                                    {msg.sql_query}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-white shadow rounded-lg p-4 w-full max-w-3xl">
                            <div className="space-y-3">
                                <Skeleton className="h-4 w-3/4" />
                                <Skeleton className="h-4 w-1/2" />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="bg-white p-4 border-t">
                <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto flex gap-4">
                    <input
                        type="text"
                        className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
                        placeholder="Type your question..."
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !newMessage.trim()}
                        className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
                    >
                        Send
                    </button>
                </form>
            </div>
        </div>
    );
}
