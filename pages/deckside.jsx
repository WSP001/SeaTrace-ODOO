/**
 * DeckSide (RECORD) - Four Pillars: Accountability
 * Catch ticket validation & GPS correlation
 * 
 * For the Commons Good 🌊
 */

import { useEffect, useState } from 'react';
import Head from 'next/head';

export default function DeckSidePage() {
  const [apiHealth, setApiHealth] = useState(null);

  useEffect(() => {
    fetch('/api/v1/health')
      .then(res => res.json())
      .then(data => setApiHealth(data))
      .catch(err => console.error('API health check failed:', err));
  }, []);

  return (
    <>
      <Head>
        <title>DeckSide (RECORD) | SeaTrace</title>
        <meta name="description" content="Catch ticket validation and GPS correlation" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📋</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">DeckSide</h1>
                <p className="text-sm text-gray-600">RECORD Phase | Four Pillars: Accountability</p>
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
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-green-900 mb-3">
              📋 Catch Ticket Validation & GPS Correlation
            </h2>
            <p className="text-gray-700 mb-4">
              DeckSide validates catch tickets against vessel AIS tracks to ensure reported 
              catch locations match actual fishing positions. This creates an immutable record 
              linking catch data to vessel movements.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">✓</span>
                <span><strong>Accountable:</strong> Every catch ticket cryptographically signed</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">✓</span>
                <span><strong>Traceable:</strong> GPS correlation creates audit trail</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">✓</span>
                <span><strong>Compliant:</strong> NMFS/NOAA data fields captured</span>
              </li>
            </ul>
          </div>

          {/* Correlation Engine */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Correlation Engine</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-blue-50 rounded">
                <span className="text-2xl">🚢</span>
                <div className="flex-1">
                  <p className="font-semibold text-sm">AIS Position Data</p>
                  <p className="text-xs text-gray-600">Vessel location + timestamp</p>
                </div>
              </div>
              <div className="flex justify-center">
                <span className="text-green-600 text-2xl">⊕</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded">
                <span className="text-2xl">📋</span>
                <div className="flex-1">
                  <p className="font-semibold text-sm">Catch Ticket</p>
                  <p className="text-xs text-gray-600">Species + weight + reported location</p>
                </div>
              </div>
              <div className="flex justify-center">
                <span className="text-gray-400">↓</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-purple-50 border-2 border-purple-600 rounded">
                <span className="text-2xl">✅</span>
                <div className="flex-1">
                  <p className="font-semibold text-sm">Validated Record</p>
                  <p className="text-xs text-gray-600">Signed + correlated + timestamped</p>
                </div>
              </div>
            </div>
          </div>

          {/* Data Pipeline Preview */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Pipeline: Hold → RECORD → Store → Exchange</h2>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex-1 bg-gray-100 border border-gray-300 rounded p-3 text-center">
                Hold<br/>
                <span className="text-xs text-gray-600">SeaSide</span>
              </div>
              <span className="text-gray-400">→</span>
              <div className="flex-1 bg-green-100 border-2 border-green-600 rounded p-3 text-center font-semibold">
                RECORD<br/>
                <span className="text-xs text-green-700">DeckSide</span>
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
              <strong>Demo Mode:</strong> Catch ticket correlation engine in development. 
              This page demonstrates the DeckSide validation architecture and accountability model.
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
