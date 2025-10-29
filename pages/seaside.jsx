/**
 * SeaSide (HOLD) - Four Pillars: Autonomy
 * Vessel registration & AIS packet ingestion entry point
 * 
 * For the Commons Good 🌊
 */

import { useEffect, useState } from 'react';
import Head from 'next/head';

export default function SeaSidePage() {
  const [apiHealth, setApiHealth] = useState(null);

  useEffect(() => {
    // Check API health on mount
    fetch('/api/v1/health')
      .then(res => res.json())
      .then(data => setApiHealth(data))
      .catch(err => console.error('API health check failed:', err));
  }, []);

  return (
    <>
      <Head>
        <title>SeaSide (HOLD) | SeaTrace</title>
        <meta name="description" content="Vessel registration and AIS packet ingestion" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🚢</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">SeaSide</h1>
                <p className="text-sm text-gray-600">HOLD Phase | Four Pillars: Autonomy</p>
              </div>
            </div>
          </div>

          {/* Status Card */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Service Status</h2>
              {apiHealth ? (
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  ✅ Operational
                </span>
              ) : (
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                  ⏳ Checking...
                </span>
              )}
            </div>
            
            {apiHealth && (
              <div className="bg-gray-50 rounded p-4">
                <p className="text-sm text-gray-600 mb-2">Build Info:</p>
                <pre className="text-xs text-gray-800 overflow-auto">
                  {JSON.stringify(apiHealth, null, 2)}
                </pre>
              </div>
            )}
          </div>

          {/* Purpose Section */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-blue-900 mb-3">
              📡 Vessel Registration & AIS Ingestion
            </h2>
            <p className="text-gray-700 mb-4">
              SeaSide is the entry point for maritime provenance data. Vessels register 
              their identity and begin transmitting AIS (Automatic Identification System) 
              packets to establish the first link in the chain of custody.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span><strong>Autonomous:</strong> Vessels self-register without central authority approval</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span><strong>Secure:</strong> Ed25519 signatures verify vessel identity</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span><strong>Observable:</strong> Prometheus metrics track ingestion rate</span>
              </li>
            </ul>
          </div>

          {/* Data Pipeline Preview */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Pipeline: HOLD → Record → Store → Exchange</h2>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex-1 bg-blue-100 border-2 border-blue-600 rounded p-3 text-center font-semibold">
                HOLD<br/>
                <span className="text-xs text-blue-700">SeaSide</span>
              </div>
              <span className="text-gray-400">→</span>
              <div className="flex-1 bg-gray-100 border border-gray-300 rounded p-3 text-center">
                Record<br/>
                <span className="text-xs text-gray-600">DeckSide</span>
              </div>
              <span className="text-gray-400">→</span>
              <div className="flex-1 bg-gray-100 border border-gray-300 rounded p-3 text-center">
                Store<br/>
                <span className="text-xs text-gray-600">DockSide</span>
              </div>
              <span className="text-gray-400">→</span>
              <div className="flex-1 bg-gray-100 border border-gray-300 rounded p-3 text-center">
                Exchange<br/>
                <span className="text-xs text-gray-600">MarketSide</span>
              </div>
            </div>
          </div>

          {/* Demo Notice */}
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <strong>Demo Mode:</strong> Full vessel data wiring in progress. 
              This page demonstrates the SeaSide service architecture and Four Pillars alignment.
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
