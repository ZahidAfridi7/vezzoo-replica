'use client';

import Link from 'next/link';
import { useAuthStore } from '@/store/auth';
import { PlusIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

export default function Dashboard() {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="py-10 px-8">
      <header className="mb-10">
        <h1 className="text-3xl font-bold leading-tight tracking-tight text-gray-900">
          Welcome back, {user?.full_name || user?.email || 'User'}!
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Ready to explore your data? Start by connecting a database or continuing a chat.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {/* Quick Action: New Connection */}
        <div className="relative flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
          <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
            <PlusIcon className="h-6 w-6" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Connect Data</h3>
          <p className="mt-2 flex-1 text-sm text-gray-500">
            Add a new database connection to start analyzing your data.
          </p>
          <div className="mt-6">
            <Link
              href="/connections/new"
              className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
            >
              Add Connection <span aria-hidden="true" className="ml-1">&rarr;</span>
            </Link>
          </div>
        </div>

        {/* Quick Action: New Chat */}
        <div className="relative flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
          <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-green-50 text-green-600">
            <ChatBubbleLeftRightIcon className="h-6 w-6" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Start Chatting</h3>
          <p className="mt-2 flex-1 text-sm text-gray-500">
            Ask questions about your data in natural language.
          </p>
          <div className="mt-6">
            <Link
              href="/chat"
              className="inline-flex items-center text-sm font-medium text-green-600 hover:text-green-500"
            >
              Go to Chat <span aria-hidden="true" className="ml-1">&rarr;</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
