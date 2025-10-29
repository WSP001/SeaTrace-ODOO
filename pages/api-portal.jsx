/**
 * SeaTrace API Portal
 * Interactive API documentation and testing interface
 * 
 * For the Commons Good 🌊
 */

import { useState } from 'react';
import Head from 'next/head';

export default function APIPortalPage() {
  const [activeEndpoint, setActiveEndpoint] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [licenseMode, setLicenseMode] = useState('commons'); // 'commons' | 'limited'

  const isLimitedView = licenseMode === 'limited';
  const commonsMetrics = [
    { label: 'Commons Fund Coverage', value: '112%', detail: 'Backstopped by MarketSide revenue tithe' },
    { label: 'Verified Trips (WAFC + GGSE)', value: '4,140', detail: '14 vessels · 45-day average trips' },
    { label: 'Sea Surface Delta', value: '+1.5°C', detail: 'Bay of Bengal 5-year anomaly (MCP agent)' },
  ];

  const investorInsights = [
    { label: '$CHECK KEY Accuracy', value: '95% ≤ 5%', detail: 'DeckSide prospectus variance' },
    { label: 'Projected Profit (Fleet)', value: '$840K', detail: '14 vessels × $60K profit per vessel' },
    { label: 'Confidence Score', value: '0.92', detail: 'Market enrichment overlay confidence' },
  ];

  const mcpSnapshot = {
    geography: 'Bay of Bengal MCP Agent',
    primaryStocks: 'Tuna · Mackerel · Cephalopods',
    climate: '+1.5°C anomaly · recovering oxygen bands',
    coverage: 'ER coverage 92% · Commons Fund pays 100%',
  };

  const handleLicenseToggle = () =>
    setLicenseMode((current) => (current === 'limited' ? 'commons' : 'limited'));

  const licenseCtaText = isLimitedView ? 'Access Premium Analytics' : 'Verify Public Chain (Free)';
  const licenseTagline = isLimitedView
    ? 'LIMITED license • MarketSide subscription controls access'
    : 'Unlimited Public Key • Commons Fund keeps verification free';

  const testEndpoint = async (endpoint) => {
    setActiveEndpoint(endpoint);
    setTestResult({ status: 'loading', message: 'Testing endpoint...' });
    
    try {
      const response = await fetch(endpoint.url);
      const data = await response.json();
      setTestResult({
        status: response.ok ? 'success' : 'error',
        statusCode: response.status,
        data: data
      });
    } catch (error) {
      setTestResult({
        status: 'error',
        message: error.message
      });
    }
  };

  return (
    <>
      <Head>
        <title>SeaTrace API Portal | Four Pillars Architecture</title>
        <meta name="description" content="Production-ready marine intelligence API endpoints for sustainable fishing and seafood traceability" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 shadow-sm">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-4xl">🌊</span>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">SeaTrace API Portal</h1>
                  <p className="text-sm text-gray-600">Four Pillars Architecture</p>
                </div>
              </div>
              
              <div className="flex gap-4">
                <a href="/docs" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition">
                  API Docs
                </a>
                <a href="/postman" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition">
                  Postman
                </a>
                <a href="/" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition">
                  Main Site
                </a>
              </div>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-12">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-4xl font-bold mb-4">SeaTrace API Portal</h2>
            <p className="text-xl mb-2">Four Pillars Architecture</p>
            <p className="text-2xl font-bold mb-6">💰 Stack Operator Valuation: $4.2M USD</p>
            <p className="text-lg opacity-90 max-w-3xl mx-auto">
              Production-ready marine intelligence API endpoints for sustainable fishing and seafood traceability
            </p>
            <div className="mt-8 flex flex-col items-center gap-3">
              <button
                type="button"
                onClick={handleLicenseToggle}
                className="rounded-full bg-white/10 px-6 py-3 text-sm font-semibold uppercase tracking-wider shadow-lg shadow-black/20 transition hover:bg-white/20"
              >
                {licenseCtaText}
              </button>
              <p className="text-sm font-medium tracking-wide text-white/80">{licenseTagline}</p>
            </div>
          </div>
        </div>

        {/* Dual-Key Toggle */}
        <section className="bg-white border-b border-gray-200 py-12">
          <div className="container mx-auto px-4 space-y-8">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-blue-600">Dual-Key Operations</p>
                <h3 className="text-2xl font-bold text-gray-900 mt-1">Commons Good + Investor Value on one rail</h3>
                <p className="text-gray-600 mt-2 max-w-2xl">
                  Toggle between the Unlimited Public Key that keeps verification free for every coastal community and the LIMITED license
                  that unlocks prospectus-grade $CHECK KEY analytics, Grafana overlays, and Codex-generated reports.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-sm font-semibold ${!isLimitedView ? 'text-blue-600' : 'text-gray-400'}`}>Commons</span>
                <button
                  type="button"
                  aria-label="Toggle license tier"
                  onClick={handleLicenseToggle}
                  className={`relative inline-flex h-10 w-20 items-center rounded-full transition ${
                    isLimitedView ? 'bg-indigo-600' : 'bg-slate-300'
                  }`}
                >
                  <span
                    className={`inline-block h-8 w-8 transform rounded-full bg-white shadow-lg transition ${
                      isLimitedView ? 'translate-x-10' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className={`text-sm font-semibold ${isLimitedView ? 'text-indigo-600' : 'text-gray-400'}`}>Investor</span>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <article className="rounded-2xl border border-gray-100 bg-gradient-to-br from-white to-blue-50 p-6 shadow">
                <header className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-blue-500">Unlimited Public Key</p>
                    <h4 className="text-xl font-bold text-gray-900">Commons Good Telemetry</h4>
                  </div>
                  <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
                    Funded by Commons Fund
                  </span>
                </header>
                <dl className="mt-6 space-y-4">
                  {commonsMetrics.map((metric) => (
                    <div key={metric.label} className="rounded-xl border border-white/60 bg-white/80 p-4 shadow-sm">
                      <dt className="text-xs font-semibold uppercase tracking-wide text-gray-500">{metric.label}</dt>
                      <dd className="text-2xl font-bold text-gray-900">{metric.value}</dd>
                      <p className="text-sm text-gray-600 mt-1">{metric.detail}</p>
                    </div>
                  ))}
                </dl>
                <div className="mt-6 rounded-xl border border-blue-100 bg-white p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">Data Commons MCP Agent</p>
                  <p className="text-sm text-gray-800 mt-2">{mcpSnapshot.geography}</p>
                  <ul className="mt-3 space-y-1 text-sm text-gray-600">
                    <li>• Primary stocks: {mcpSnapshot.primaryStocks}</li>
                    <li>• Climate signal: {mcpSnapshot.climate}</li>
                    <li>• Coverage pledge: {mcpSnapshot.coverage}</li>
                  </ul>
                </div>
              </article>

              <article
                className={`relative rounded-2xl border p-6 transition ${
                  isLimitedView
                    ? 'border-indigo-200 bg-gradient-to-br from-white to-indigo-50 shadow-2xl shadow-indigo-100'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                {!isLimitedView && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center rounded-2xl bg-white/70 backdrop-blur-sm">
                    <span className="rounded-full bg-indigo-100 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-indigo-700">
                      LIMITED license required
                    </span>
                    <p className="mt-2 text-sm text-gray-600">Toggle to investor mode to unlock premium analytics.</p>
                  </div>
                )}
                <header className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-indigo-500">LIMITED Private Key</p>
                    <h4 className="text-xl font-bold text-gray-900">Investor Monetization Stack</h4>
                  </div>
                  <span className="rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold text-indigo-700">
                    MarketSide Subscription
                  </span>
                </header>
                <dl className="mt-6 space-y-4">
                  {investorInsights.map((metric) => (
                    <div key={metric.label} className="rounded-xl border border-white/60 bg-white/90 p-4 shadow-sm">
                      <dt className="text-xs font-semibold uppercase tracking-wide text-gray-500">{metric.label}</dt>
                      <dd className="text-2xl font-bold text-gray-900">{metric.value}</dd>
                      <p className="text-sm text-gray-600 mt-1">{metric.detail}</p>
                    </div>
                  ))}
                </dl>
                <div className="mt-6 flex flex-wrap gap-3">
                  <span className="rounded-full bg-gray-900 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
                    Prospectus $CHECK KEY
                  </span>
                  <span className="rounded-full bg-indigo-600/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-indigo-700">
                    Grafana KPIs
                  </span>
                  <span className="rounded-full bg-pink-600/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-pink-700">
                    Codex Reports
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setLicenseMode('limited')}
                  className={`mt-6 w-full rounded-xl px-4 py-3 text-center text-sm font-semibold uppercase tracking-wide transition ${
                    isLimitedView
                      ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200 hover:bg-indigo-700'
                      : 'bg-gray-300 text-gray-600'
                  }`}
                >
                  {isLimitedView ? 'Provision LIMITED Access' : 'Slide to LIMITED to unlock'}
                </button>
              </article>
            </div>
          </div>
        </section>

        {/* API Sections */}
        <div className="container mx-auto px-4 py-12">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* SeaSide (HOLD) */}
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition">
              <div className="bg-blue-50 border-b border-blue-200 px-6 py-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">🌊</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">SeaSide (HOLD)</h3>
                    <p className="text-sm text-gray-600">Vessel tracking and initial data capture</p>
                  </div>
                </div>
              </div>
              
              <div className="p-6 space-y-3">
                <EndpointCard
                  method="GET"
                  path="/api/v1/seaside/vessels"
                  description="List all registered vessels"
                  onTest={() => testEndpoint({ url: '/api/v1/seaside/vessels', method: 'GET' })}
                />
                <EndpointCard
                  method="GET"
                  path="/api/v1/seaside/vessels/{id}"
                  description="Get vessel details by ID"
                  onTest={() => testEndpoint({ url: '/api/v1/seaside/vessels/demo-001', method: 'GET' })}
                />
                <EndpointCard
                  method="POST"
                  path="/api/v1/seaside/vessels/{id}/positions"
                  description="Submit AIS position data"
                  onTest={() => testEndpoint({ url: '/api/v1/seaside/vessels/demo-001/positions', method: 'POST' })}
                />
                <EndpointCard
                  method="POST"
                  path="/api/v1/seaside/quality/score"
                  description="Calculate quality score"
                  onTest={() => testEndpoint({ url: '/api/v1/seaside/quality/score', method: 'POST' })}
                />
              </div>
              
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                <a href="/seaside" className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                  🔍 Learn more about SeaSide →
                </a>
              </div>
            </div>

            {/* DeckSide (RECORD) */}
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition">
              <div className="bg-green-50 border-b border-green-200 px-6 py-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">📊</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">DeckSide (RECORD)</h3>
                    <p className="text-sm text-gray-600">Catch verification and certification</p>
                  </div>
                </div>
              </div>
              
              <div className="p-6 space-y-3">
                <EndpointCard
                  method="GET"
                  path="/api/v1/deckside/catches"
                  description="List verified catches"
                  onTest={() => testEndpoint({ url: '/api/v1/deckside/catches', method: 'GET' })}
                />
                <EndpointCard
                  method="GET"
                  path="/api/v1/deckside/catches/{id}"
                  description="Get catch details"
                  onTest={() => testEndpoint({ url: '/api/v1/deckside/catches/catch-001', method: 'GET' })}
                />
                <EndpointCard
                  method="POST"
                  path="/api/v1/deckside/catches"
                  description="Submit new catch ticket"
                  onTest={() => testEndpoint({ url: '/api/v1/deckside/catches', method: 'POST' })}
                />
                <EndpointCard
                  method="POST"
                  path="/api/v1/deckside/qrcode"
                  description="Generate catch QR code"
                  onTest={() => testEndpoint({ url: '/api/v1/deckside/qrcode', method: 'POST' })}
                />
              </div>
              
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                <a href="/deckside" className="text-green-600 hover:text-green-800 font-medium text-sm">
                  🔍 Learn more about DeckSide →
                </a>
              </div>
            </div>

            {/* DockSide (STORE) */}
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition">
              <div className="bg-purple-50 border-b border-purple-200 px-6 py-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">🏗️</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">DockSide (STORE)</h3>
                    <p className="text-sm text-gray-600">Supply chain and storage management</p>
                  </div>
                </div>
              </div>
              
              <div className="p-6 space-y-3">
                <EndpointCard
                  method="GET"
                  path="/api/v1/dockside/processing"
                  description="List processing facilities"
                  onTest={() => testEndpoint({ url: '/api/v1/dockside/processing', method: 'GET' })}
                />
                <EndpointCard
                  method="GET"
                  path="/api/v1/dockside/processing/{id}"
                  description="Get facility details"
                  onTest={() => testEndpoint({ url: '/api/v1/dockside/processing/facility-001', method: 'GET' })}
                />
                <EndpointCard
                  method="POST"
                  path="/api/v1/dockside/processing"
                  description="Submit processing record"
                  onTest={() => testEndpoint({ url: '/api/v1/dockside/processing', method: 'POST' })}
                />
                <EndpointCard
                  method="GET"
                  path="/api/v1/dockside/bone/files"
                  description="Get BONE blockchain files"
                  onTest={() => testEndpoint({ url: '/api/v1/dockside/bone/files', method: 'GET' })}
                />
              </div>
              
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                <a href="/dockside" className="text-purple-600 hover:text-purple-800 font-medium text-sm">
                  🔍 Learn more about DockSide →
                </a>
              </div>
            </div>

            {/* MarketSide (EXCHANGE) */}
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition">
              <div className="bg-orange-50 border-b border-orange-200 px-6 py-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">🏪</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">MarketSide (EXCHANGE)</h3>
                    <p className="text-sm text-gray-600">Consumer verification and market integration</p>
                  </div>
                </div>
              </div>
              
              <div className="p-6 space-y-3">
                <EndpointCard
                  method="GET"
                  path="/api/v1/marketside/verification"
                  description="Get verification status"
                  onTest={() => testEndpoint({ url: '/api/v1/marketside/verification', method: 'GET' })}
                />
                <EndpointCard
                  method="POST"
                  path="/api/v1/marketside/qr/verify"
                  description="Verify product QR code"
                  onTest={() => testEndpoint({ url: '/api/v1/marketside/qr/verify', method: 'POST' })}
                />
                <EndpointCard
                  method="GET"
                  path="/api/v1/marketside/consumer/info"
                  description="Get consumer-facing info"
                  onTest={() => testEndpoint({ url: '/api/v1/marketside/consumer/info', method: 'GET' })}
                />
              </div>
              
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                <a href="/marketside" className="text-orange-600 hover:text-orange-800 font-medium text-sm">
                  🔍 Learn more about MarketSide →
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Documentation & Tools Section */}
        <div className="bg-gray-50 py-12">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-8">🚀 API Documentation & Tools</h2>
            <p className="text-center text-gray-600 mb-8">
              Comprehensive documentation and testing tools for SeaTrace Four Pillars API
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <ToolCard
                icon="📋"
                title="OpenAPI Spec"
                description="Complete API specification with schemas and examples"
                link="/api/openapi.json"
                linkText="View Spec"
              />
              <ToolCard
                icon="📧"
                title="Postman Collection"
                description="Production-ready Postman collection for all endpoints"
                link="/api/postman-collection.json"
                linkText="Import Collection"
              />
              <ToolCard
                icon="🛠️"
                title="SDK Downloads"
                description="Client libraries for Python, JavaScript, and .NET"
                link="/sdk"
                linkText="Download SDKs"
              />
              <ToolCard
                icon="🔐"
                title="Authentication"
                description="API key management and JWT token authentication"
                link="/auth-guide"
                linkText="Auth Guide"
              />
            </div>
          </div>
        </div>

        {/* Test Result Modal */}
        {testResult && (
          <div className="fixed bottom-4 right-4 w-96 bg-white border border-gray-300 rounded-lg shadow-xl p-6 z-50">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-bold">Test Result</h3>
              <button
                onClick={() => setTestResult(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            {testResult.status === 'loading' && (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Testing endpoint...</p>
              </div>
            )}
            
            {testResult.status === 'success' && (
              <div>
                <div className="mb-3 p-2 bg-green-100 text-green-800 rounded text-sm font-medium">
                  ✅ Status: {testResult.statusCode} OK
                </div>
                <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-64">
                  {JSON.stringify(testResult.data, null, 2)}
                </pre>
              </div>
            )}
            
            {testResult.status === 'error' && (
              <div className="p-3 bg-red-100 text-red-800 rounded text-sm">
                ❌ Error: {testResult.message || `Status ${testResult.statusCode}`}
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-8">
          <div className="container mx-auto px-4 text-center">
            <p className="mb-2">© 2024 SeaTrace API Portal - WorldSeafoodProducers.com</p>
            <p className="text-gray-400">
              Four Pillars Architecture | Stack Operator Validated | Production Ready
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}

// Endpoint Card Component
function EndpointCard({ method, path, description, onTest }) {
  const methodColors = {
    GET: 'bg-blue-100 text-blue-800 border-blue-300',
    POST: 'bg-green-100 text-green-800 border-green-300',
    PUT: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    DELETE: 'bg-red-100 text-red-800 border-red-300'
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition group">
      <span className={`px-2 py-1 text-xs font-bold rounded border ${methodColors[method]}`}>
        {method}
      </span>
      <div className="flex-1">
        <code className="text-sm font-mono text-gray-800">{path}</code>
        <p className="text-xs text-gray-600 mt-1">{description}</p>
      </div>
      <button
        onClick={onTest}
        className="px-3 py-1 text-xs font-medium bg-white border border-gray-300 rounded hover:bg-gray-50 hover:border-blue-400 transition opacity-0 group-hover:opacity-100"
      >
        Test
      </button>
    </div>
  );
}

// Tool Card Component
function ToolCard({ icon, title, description, link, linkText }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-lg font-bold mb-2">{title}</h3>
      <p className="text-sm text-gray-600 mb-4">{description}</p>
      <a
        href={link}
        className="inline-block px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition"
      >
        {linkText}
      </a>
    </div>
  );
}
