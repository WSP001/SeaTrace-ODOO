/**
 * DockSide (STORE) - Four Pillars: Optimization
 * Cold storage tracking & quality assurance
 * 
 * For the Commons Good 🌊
 */

import { useEffect, useState } from 'react';
import Head from 'next/head';

export default function DockSidePage() {
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
        <title>DockSide (STORE) | SeaTrace</title>
        <meta name="description" content="Cold storage tracking and quality assurance" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🏭</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">DockSide</h1>
                <p className="text-sm text-gray-600">STORE Phase | Four Pillars: Optimization</p>
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
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-purple-900 mb-3">
              🏭 Cold Storage Tracking & Quality Assurance
            </h2>
            <p className="text-gray-700 mb-4">
              DockSide monitors product through processing and storage facilities, tracking 
              temperature, humidity, and chain-of-custody from dock to distribution. Optimizes 
              logistics and reduces waste through real-time condition monitoring.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1">✓</span>
                <span><strong>Optimized:</strong> Real-time sensor data reduces spoilage</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1">✓</span>
                <span><strong>Efficient:</strong> Automated alerts for out-of-spec conditions</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1">✓</span>
                <span><strong>Transparent:</strong> Full storage history accessible to buyers</span>
              </li>
            </ul>
          </div>

          {/* Storage Monitoring */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Cold Storage Monitoring</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🌡️</span>
                  <h3 className="font-semibold text-sm">Temperature</h3>
                </div>
                <p className="text-2xl font-bold text-blue-700">-18°C</p>
                <p className="text-xs text-gray-600 mt-1">Target: -18°C ±2°C</p>
                <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                  ✓ In Spec
                </span>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">💧</span>
                  <h3 className="font-semibold text-sm">Humidity</h3>
                </div>
                <p className="text-2xl font-bold text-blue-700">65%</p>
                <p className="text-xs text-gray-600 mt-1">Target: 60-70%</p>
                <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                  ✓ In Spec
                </span>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">⏱️</span>
                  <h3 className="font-semibold text-sm">Duration</h3>
                </div>
                <p className="text-2xl font-bold text-blue-700">14 days</p>
                <p className="text-xs text-gray-600 mt-1">Avg: 7-21 days</p>
                <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                  ✓ Optimal
                </span>
              </div>
            </div>
          </div>

          {/* Optimization Metrics */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Optimization Metrics</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                <span className="text-sm font-medium">Spoilage Rate</span>
                <span className="text-green-700 font-bold">↓ 0.3% (industry avg: 2.5%)</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                <span className="text-sm font-medium">Energy Efficiency</span>
                <span className="text-green-700 font-bold">↑ 18% vs baseline</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                <span className="text-sm font-medium">Traceability Audit Time</span>
                <span className="text-green-700 font-bold">↓ 3 hrs → 15 min</span>
              </div>
            </div>
          </div>

          {/* Data Pipeline Preview */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Pipeline: Hold → Record → STORE → Exchange</h2>
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
              <div className="flex-1 bg-purple-100 border-2 border-purple-600 rounded p-3 text-center font-semibold">
                STORE<br/>
                <span className="text-xs text-purple-700">DockSide</span>
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
              <strong>Demo Mode:</strong> Sensor integration and cold storage tracking in progress. 
              This page demonstrates DockSide optimization capabilities and IoT monitoring architecture.
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
