'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface ChatSession {
    id: number;
    title: string;
    created_at: string;
}

interface Connection {
    id: number;
    name: string;
}

export default function ChatListPage() {
    const [sessions, setSessions] = useState<ChatSession[]>([]);
    const [connections, setConnections] = useState<Connection[]>([]);
    const [selectedConnection, setSelectedConnection] = useState<string>('');
    const [message, setMessage] = useState('');
    const router = useRouter();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [sessRes, connRes] = await Promise.all([
                    api.get('/chat/sessions'),
                    api.get('/connections/')
                ]);
                setSessions(sessRes.data);
                setConnections(connRes.data);
                if (connRes.data.length > 0) {
                    setSelectedConnection(connRes.data[0].id.toString());
                }
            } catch (error) {
                console.error('Failed to fetch data', error);
            }
        };
        fetchData();
    }, []);

    const handleNewChat = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedConnection || !message) return;

        try {
            const response = await api.post('/chat/sessions', {
                connection_id: parseInt(selectedConnection),
                message: message
            });
            router.push(`/chat/${response.data.id}`);
        } catch (error) {
            console.error('Failed to create session', error);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="mx-auto max-w-4xl">
                <h2 className="text-2xl font-bold mb-6">Chat with your Data</h2>

                {/* New Chat Form */}
                <div className="bg-white p-6 rounded-lg shadow mb-8">
                    <h3 className="text-lg font-medium mb-4">Start a new conversation</h3>
                    <form onSubmit={handleNewChat} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Select Connection</label>
                            <select
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                                value={selectedConnection}
                                onChange={(e) => setSelectedConnection(e.target.value)}
                            >
                                {connections.map((conn) => (
                                    <option key={conn.id} value={conn.id}>{conn.name}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Your Question</label>
                            <input
                                type="text"
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                                placeholder="e.g., How many users signed up last week?"
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                        >
                            Ask
                        </button>
                    </form>
                </div>

                {/* Recent Sessions */}
                <h3 className="text-lg font-medium mb-4">Recent Conversations</h3>
                <div className="space-y-4">
                    {sessions.map((session) => (
                        <Link key={session.id} href={`/chat/${session.id}`} className="block">
                            <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
                                <p className="font-medium text-gray-900">{session.title || 'Untitled Chat'}</p>
                                <p className="text-sm text-gray-500">{new Date(session.created_at).toLocaleString()}</p>
                            </div>
                        </Link>
                    ))}
                    {sessions.length === 0 && <p className="text-gray-500">No conversations yet.</p>}
                </div>
            </div>
        </div>
    );
}
