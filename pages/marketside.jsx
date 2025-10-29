/**
 * MarketSide (EXCHANGE) - Four Pillars: Collaboration
 * Market access & buyer verification
 * 
 * For the Commons Good 🌊
 */

import { useEffect, useState } from 'react';
import Head from 'next/head';

export default function MarketSidePage() {
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
        <title>MarketSide (EXCHANGE) | SeaTrace</title>
        <meta name="description" content="Market access and buyer verification" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🤝</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">MarketSide</h1>
                <p className="text-sm text-gray-600">EXCHANGE Phase | Four Pillars: Collaboration</p>
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
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-orange-900 mb-3">
              🤝 Market Access & Buyer Verification
            </h2>
            <p className="text-gray-700 mb-4">
              MarketSide connects verified sustainable catch with premium buyers, providing 
              transparent provenance data that enables collaboration across the supply chain. 
              Buyers access full chain-of-custody records to verify sustainability claims.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-orange-600 mt-1">✓</span>
                <span><strong>Collaborative:</strong> Multi-stakeholder access to provenance data</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 mt-1">✓</span>
                <span><strong>Verified:</strong> Buyer credentials validated via mTLS</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 mt-1">✓</span>
                <span><strong>Transparent:</strong> Full audit trail from catch to market</span>
              </li>
            </ul>
          </div>

          {/* Stakeholder Network */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Collaborative Network</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg text-center">
                <span className="text-3xl block mb-2">🚢</span>
                <p className="text-sm font-semibold">Fishermen</p>
                <p className="text-xs text-gray-600 mt-1">Data Providers</p>
              </div>
              
              <div className="p-4 bg-green-50 rounded-lg text-center">
                <span className="text-3xl block mb-2">🏢</span>
                <p className="text-sm font-semibold">Processors</p>
                <p className="text-xs text-gray-600 mt-1">Value-Add</p>
              </div>
              
              <div className="p-4 bg-purple-50 rounded-lg text-center">
                <span className="text-3xl block mb-2">🏪</span>
                <p className="text-sm font-semibold">Distributors</p>
                <p className="text-xs text-gray-600 mt-1">Logistics</p>
              </div>
              
              <div className="p-4 bg-orange-50 rounded-lg text-center">
                <span className="text-3xl block mb-2">🛒</span>
                <p className="text-sm font-semibold">Retailers</p>
                <p className="text-xs text-gray-600 mt-1">End Buyers</p>
              </div>
            </div>
          </div>

          {/* Value Proposition */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Value Exchange</h2>
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-sm mb-1">For Fishermen</h3>
                <p className="text-sm text-gray-700">
                  Premium market access (15-30% price uplift) for verified sustainable catch
                </p>
              </div>
              
              <div className="border-l-4 border-green-500 pl-4">
                <h3 className="font-semibold text-sm mb-1">For Buyers</h3>
                <p className="text-sm text-gray-700">
                  Verified sustainability claims reduce regulatory risk and enable green marketing
                </p>
              </div>
              
              <div className="border-l-4 border-purple-500 pl-4">
                <h3 className="font-semibold text-sm mb-1">For Regulators</h3>
                <p className="text-sm text-gray-700">
                  Real-time compliance monitoring replaces costly manual audits
                </p>
              </div>
              
              <div className="border-l-4 border-orange-500 pl-4">
                <h3 className="font-semibold text-sm mb-1">For Commons</h3>
                <p className="text-sm text-gray-700">
                  12.5% EMR metering funds sustainable fisheries management
                </p>
              </div>
            </div>
          </div>

          {/* Data Pipeline Preview */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Pipeline: Hold → Record → Store → EXCHANGE</h2>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex-1 bg-gray-100 border border-gray-300 rounded p-3 text-center">
                Hold<br/>
                <span className="text-xs text-gray-600">SeaSide</span>
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
              <div className="flex-1 bg-orange-100 border-2 border-orange-600 rounded p-3 text-center font-semibold">
                EXCHANGE<br/>
                <span className="text-xs text-orange-700">MarketSide</span>
              </div>
            </div>
          </div>

          {/* Demo Notice */}
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <strong>Demo Mode:</strong> Buyer marketplace and pricing engine in development. 
              This page demonstrates MarketSide collaboration model and stakeholder value exchange.
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
