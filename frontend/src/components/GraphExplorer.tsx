'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';

// Dynamically import ForceGraph2D to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
    ssr: false,
    loading: () => <div className="flex items-center justify-center h-full">Loading Graph...</div>
}) as any;

interface GraphNode {
    id: number;
    name: string;
    type: string;
    metadata_json: string;
    // ForceGraph adds these
    x?: number;
    y?: number;
    val?: number; // size
}

interface GraphEdge {
    source: number | GraphNode; // ID or Node object after processing
    target: number | GraphNode;
    type: string;
    metadata_json: string;
}

interface GraphData {
    nodes: GraphNode[];
    links: GraphEdge[];
}

interface GraphExplorerProps {
    data: GraphData;
}

export default function GraphExplorer({ data }: GraphExplorerProps) {
    const graphRef = useRef<any>(null);
    const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

    // Parse metadata for display
    const getColumns = (node: GraphNode) => {
        try {
            const meta = JSON.parse(node.metadata_json);
            return meta.columns || [];
        } catch (e) {
            return [];
        }
    };

    return (
        <div className="relative w-full h-screen bg-gray-900 text-white overflow-hidden">
            <ForceGraph2D
                ref={graphRef}
                graphData={data}
                nodeLabel="name"
                nodeColor={(node: any) => node.type === 'table' ? '#4f46e5' : '#10b981'}
                nodeRelSize={6}
                linkColor={() => '#4b5563'}
                linkDirectionalArrowLength={3.5}
                linkDirectionalArrowRelPos={1}
                onNodeClick={(node: any) => {
                    setSelectedNode(node);
                    // Center view on node
                    graphRef.current?.centerAt(node.x, node.y, 1000);
                    graphRef.current?.zoom(2, 2000);
                }}
                onBackgroundClick={() => setSelectedNode(null)}
            />

            {/* Side Panel for Node Details */}
            {selectedNode && (
                <div className="absolute right-0 top-0 h-full w-80 bg-gray-800 shadow-xl p-6 overflow-y-auto border-l border-gray-700 transition-transform transform translate-x-0">
                    <div className="flex justify-between items-start mb-4">
                        <h2 className="text-xl font-bold break-words">{selectedNode.name}</h2>
                        <button
                            onClick={() => setSelectedNode(null)}
                            className="text-gray-400 hover:text-white"
                        >
                            ✕
                        </button>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Type</span>
                            <p className="text-sm">{selectedNode.type}</p>
                        </div>

                        <div>
                            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Columns</span>
                            <ul className="mt-2 space-y-2">
                                {getColumns(selectedNode).map((col: any, idx: number) => (
                                    <li key={idx} className="flex justify-between text-sm border-b border-gray-700 pb-1">
                                        <span className="font-medium">{col.name}</span>
                                        <span className="text-gray-400 text-xs font-mono">{col.type}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
