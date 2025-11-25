'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';

interface Connection {
    id: number;
    name: string;
    db_type: string;
    host: string;
    database_name: string;
}

export default function ConnectionsPage() {
    const [connections, setConnections] = useState<Connection[]>([]);
    const router = useRouter();

    useEffect(() => {
        const fetchConnections = async () => {
            try {
                const response = await api.get('/connections/');
                setConnections(response.data);
            } catch (error) {
                console.error('Failed to fetch connections', error);
            }
        };
        fetchConnections();
    }, []);

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="mx-auto max-w-7xl">
                <div className="md:flex md:items-center md:justify-between">
                    <div className="min-w-0 flex-1">
                        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
                            Database Connections
                        </h2>
                    </div>
                    <div className="mt-4 flex md:ml-4 md:mt-0">
                        <Link
                            href="/connections/new"
                            className="ml-3 inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                        >
                            Add Connection
                        </Link>
                    </div>
                </div>

                <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {connections.map((conn) => (
                        <div key={conn.id} className="overflow-hidden rounded-lg bg-white shadow">
                            <div className="px-4 py-5 sm:p-6">
                                <h3 className="text-lg font-medium leading-6 text-gray-900">{conn.name}</h3>
                                <div className="mt-2 max-w-xl text-sm text-gray-500">
                                    <p>Type: {conn.db_type}</p>
                                    <p>Host: {conn.host}</p>
                                    <p>Database: {conn.database_name}</p>
                                </div>
                                <div className="mt-5">
                                    <button
                                        type="button"
                                        className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                                        onClick={() => router.push(`/connections/${conn.id}`)}
                                    >
                                        View Details
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
