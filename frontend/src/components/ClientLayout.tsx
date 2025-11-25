'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import Sidebar from './Sidebar';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, fetchUser } = useAuthStore();
    const router = useRouter();
    const pathname = usePathname();
    const [loading, setLoading] = useState(true);

    const isPublicPath = ['/login', '/signup'].includes(pathname);

    useEffect(() => {
        const initAuth = async () => {
            if (isAuthenticated) {
                await fetchUser();
            } else if (!isPublicPath) {
                router.push('/login');
            }
            setLoading(false);
        };
        initAuth();
    }, [isAuthenticated, isPublicPath, router, fetchUser]);

    if (loading) {
        return <div className="flex h-screen items-center justify-center">Loading...</div>;
    }

    if (isPublicPath) {
        return <>{children}</>;
    }

    return (
        <div className="flex h-screen bg-gray-50">
            <Sidebar />
            <main className="flex-1 ml-64 overflow-y-auto">
                {children}
            </main>
        </div>
    );
}
