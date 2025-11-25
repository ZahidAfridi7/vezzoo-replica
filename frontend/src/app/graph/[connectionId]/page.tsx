'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import api from '@/lib/api';
import GraphExplorer from '@/components/GraphExplorer';
import Link from 'next/link';

export default function GraphPage() {
    const params = useParams();
    const connectionId = params.connectionId;
    const [graphData, setGraphData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!connectionId) return;

        const fetchGraph = async () => {
            try {
                const response = await api.get(`/graph/${connectionId}`);
                // Transform for ForceGraph: needs 'links' instead of 'edges'
                setGraphData({
                    nodes: response.data.nodes,
                    links: response.data.edges.map((e: any) => ({
                        ...e,
                        source: e.source_id, // ForceGraph will replace these with node objects
                        target: e.target_id
                    }))
                });
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Failed to load graph');
            } finally {
                setLoading(false);
            }
        };

        fetchGraph();
    }, [connectionId]);

    if (loading) return <div className="flex h-screen items-center justify-center bg-gray-900 text-white">Loading Graph...</div>;
    if (error) return <div className="flex h-screen items-center justify-center bg-gray-900 text-red-500">{error}</div>;
    if (!graphData) return <div className="flex h-screen items-center justify-center bg-gray-900 text-white">No data found</div>;

    return (
        <div className="relative h-screen w-full">
            <div className="absolute top-4 left-4 z-10">
                <Link href="/connections" className="bg-gray-800 text-white px-4 py-2 rounded shadow hover:bg-gray-700">
                    ← Back
                </Link>
            </div>
            <GraphExplorer data={graphData} />
        </div>
    );
}
