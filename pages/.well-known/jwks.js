import crypto from 'crypto';

const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes
let cache = {
  expiresAt: 0,
  body: '',
  etag: '',
  lastModified: '',
};

const b64Url = (buffer) =>
  buffer
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');

const decodeAnyBase64 = (value) => {
  const normalized = value.replace(/\s+/g, '').replace(/-/g, '+').replace(/_/g, '/');
  const pad = (4 - (normalized.length % 4)) % 4;
  return Buffer.from(normalized + '='.repeat(pad), 'base64');
};

const kidFromX = (xB64Url) =>
  crypto.createHash('sha256').update(xB64Url, 'utf8').digest('hex').slice(0, 16);

const loadKeysFromEnv = () => {
  const result = [];

  const jwksJson = process.env.SEATRACE_JWKS_JSON;
  if (jwksJson) {
    try {
      const parsed = JSON.parse(jwksJson);
      for (const key of parsed.keys ?? []) {
        if (key.kty === 'OKP' && key.crv === 'Ed25519' && key.x) {
          result.push({
            kid: key.kid || kidFromX(key.x),
            raw: decodeAnyBase64(key.x),
          });
        }
      }
      if (result.length) {
        return result;
      }
    } catch (error) {
      console.warn('[jwks] Failed to parse SEATRACE_JWKS_JSON', error);
    }
  }

  const verifyKeys = process.env.SEATRACE_VERIFY_KEYS;
  if (verifyKeys) {
    for (const entry of verifyKeys.split(',')) {
      const value = entry.trim();
      if (!value) continue;
      if (value.includes(':')) {
        const [kid, raw] = value.split(':', 2);
        result.push({ kid: kid.trim(), raw: decodeAnyBase64(raw.trim()) });
      } else {
        const raw = decodeAnyBase64(value);
        result.push({ kid: kidFromX(b64Url(raw)), raw });
      }
    }
    if (result.length) {
      return result;
    }
  }

  const single = process.env.SEATRACE_VERIFY_KEY;
  if (single) {
    const raw = decodeAnyBase64(single);
    return [{ kid: kidFromX(b64Url(raw)), raw }];
  }

  return [];
};

const buildJwksPayload = () => {
  const keys = loadKeysFromEnv().map(({ kid, raw }) => ({
    kty: 'OKP',
    crv: 'Ed25519',
    alg: 'EdDSA',
    use: 'sig',
    kid,
    x: b64Url(raw),
  }));

  return JSON.stringify({ keys }, null, 2);
};

const refreshCache = () => {
  const body = buildJwksPayload();
  cache.body = body;
  cache.etag = `"${crypto.createHash('sha256').update(body).digest('hex').slice(0, 20)}"`;
  cache.lastModified = new Date().toUTCString();
  cache.expiresAt = Date.now() + CACHE_TTL_MS;
};

export default function handler(req, res) {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.setHeader('Allow', 'GET, HEAD');
    return res.status(405).end();
  }

  if (Date.now() > cache.expiresAt || !cache.body) {
    refreshCache();
  }

  if (req.headers['if-none-match'] === cache.etag) {
    return res.status(304).end();
  }

  res.setHeader('Content-Type', 'application/jwk-set+json; charset=utf-8');
  res.setHeader('Cache-Control', 'public, max-age=300, stale-while-revalidate=60');
  res.setHeader('ETag', cache.etag);
  res.setHeader('Last-Modified', cache.lastModified);

  if (req.method === 'HEAD') {
    return res.status(200).end();
  }

  return res.status(200).send(cache.body);
}
