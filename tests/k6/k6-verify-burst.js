import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost';
const PATH = __ENV.PATH || '/api/v1/marketside/qr/verify';
const LICENSE_ID = __ENV.LICENSE_ID || 'pul-demo-1';
const QR_CODE = __ENV.QR_CODE || 'DEMO-QR-0001';
const EXPECTED_LIMIT = Number(__ENV.RL_LIMIT || '100');

const hits2xx = new Counter('verify_hits_2xx');
const hits429 = new Counter('verify_hits_429');
const duration = new Trend('verify_duration_ms');

export const options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '30s', target: 150 },
    { duration: '60s', target: 150 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],
    verify_duration_ms: ['p(95)<800'],
    verify_hits_429: ['count>0'], // limiter should fire at least once
  },
};

export default function () {
  const payload = JSON.stringify({ qr_code: QR_CODE });
  const traceId = `${__VU.toString(16).padStart(2, '0')}${Date.now().toString(16)}`.slice(0, 16);
  const headers = {
    'Content-Type': 'application/json',
    'X-License-ID': LICENSE_ID,
    traceparent: `00-${traceId}-00`,
  };

  const response = http.post(`${BASE_URL}${PATH}`, payload, { headers });
  duration.add(response.timings.duration);

  const headerCheck = check(response, {
    'rate limit headers present': (r) =>
      ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset'].every(
        (key) => r.headers[key] !== undefined,
      ),
  });

  if (!headerCheck) {
    console.warn('Missing rate limit headers', response.headers);
  }

  if (response.status === 200) {
    hits2xx.add(1);
    check(response, {
      'verify flag true': (r) => r.json('verified') === true,
    });
  } else if (response.status === 429) {
    hits429.add(1);
    const retryAfter = Number(response.headers['Retry-After'] || '0');
    if (retryAfter > 0) {
      sleep(retryAfter);
    }
  } else {
    check(response, {
      'no server errors': (r) => r.status < 500,
    });
  }

  const remaining = Number(response.headers['X-RateLimit-Remaining'] || EXPECTED_LIMIT);
  if (remaining < 0) {
    console.warn('Limiter reported negative remaining quota', remaining);
  }
}
