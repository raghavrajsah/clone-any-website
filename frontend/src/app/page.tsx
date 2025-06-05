'use client';

import { useState } from 'react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [previewHtml, setPreviewHtml] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/clone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });
      
      const data = await response.json();
      setPreviewHtml(data.html);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to clone website. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Website Cloner
          </h1>
          <p className="text-lg text-gray-600">
            Enter a URL to clone its design and content
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="flex gap-4">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              required
              className="flex-1 rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Cloning...' : 'Clone Website'}
            </button>
          </div>
        </form>

        {previewHtml && (
          <div className="mt-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Preview
            </h2>
            <div className="border border-gray-200 rounded-lg p-4 bg-white">
              <iframe
                srcDoc={previewHtml}
                className="w-full h-[600px] border-0"
                title="Cloned Website Preview"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
