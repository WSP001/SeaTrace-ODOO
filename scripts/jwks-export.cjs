#!/usr/bin/env node
/**
 * JWKS Exporter for SeaTrace Commons
 * 
 * Purpose: Export public JWK (JSON Web Key) from private key (RSA or EC)
 * Classification: PUBLIC-UNLIMITED (no private keys exposed)
 * 
 * Usage:
 *   node scripts/jwks-export.cjs ./keys/private.pem ./staging/.well-known/jwks.json kid-001
 * 
 * Security:
 *   - Reads PRIVATE key file (keep secure!)
 *   - Exports ONLY public key components
 *   - Validates key type (RSA or EC only)
 *   - Sets appropriate 'use' and 'alg' fields
 * 
 * Dependencies: Node.js 18+ (uses node:crypto, node:fs, node:path)
 * 
 * FOR THE COMMONS GOOD! 🌍🐟🚀
 */

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");

// Parse command-line arguments
const [, , pemPath, outPath, kid = "kid-001"] = process.argv;

// Validate arguments
if (!pemPath || !outPath) {
  console.error("❌ Usage: node scripts/jwks-export.cjs <private.pem> <out.json> [kid]");
  console.error("");
  console.error("Example:");
  console.error("  node scripts/jwks-export.cjs ./keys/private.pem ./staging/.well-known/jwks.json kid-001");
  console.error("");
  console.error("Arguments:");
  console.error("  <private.pem>  Path to private key file (PEM format)");
  console.error("  <out.json>     Output path for JWKS file");
  console.error("  [kid]          Key ID (optional, default: kid-001)");
  process.exit(1);
}

// Validate input file exists
if (!fs.existsSync(pemPath)) {
  console.error(`❌ Error: Private key file not found: ${pemPath}`);
  process.exit(2);
}

try {
  console.log("🔐 Loading private key from:", pemPath);
  
  // Load private key PEM
  const privPem = fs.readFileSync(pemPath, "utf8");
  
  // Create private key object
  const priv = crypto.createPrivateKey({ key: privPem });
  
  // Derive public key from private key
  const pub = crypto.createPublicKey(priv);
  
  // Export public key as JWK (JSON Web Key)
  const pubJwk = pub.export({ format: "jwk" });
  
  console.log("📋 Key type detected:", pubJwk.kty);
  
  // Normalize to a public signing JWK
  let jwk;
  
  if (pubJwk.kty === "RSA") {
    // RSA public key - extract n (modulus) and e (exponent) only
    jwk = {
      kty: "RSA",
      n: pubJwk.n,
      e: pubJwk.e,
      use: "sig",      // Signature verification
      alg: "RS256",    // RSA with SHA-256
      kid: kid
    };
    console.log("✅ RSA key exported (RS256)");
    
  } else if (pubJwk.kty === "EC") {
    // Elliptic Curve public key - extract curve, x, y only
    const namedCurve = pub.asymmetricKeyDetails?.namedCurve;
    let alg;
    
    // Map curve to algorithm
    if (namedCurve === "prime256v1" || namedCurve === "P-256") {
      alg = "ES256"; // ECDSA with SHA-256
    } else if (namedCurve === "secp384r1" || namedCurve === "P-384") {
      alg = "ES384"; // ECDSA with SHA-384
    } else if (namedCurve === "secp521r1" || namedCurve === "P-521") {
      alg = "ES512"; // ECDSA with SHA-512
    } else {
      console.warn(`⚠️  Unknown curve: ${namedCurve}, defaulting to ES256`);
      alg = "ES256";
    }
    
    jwk = {
      kty: "EC",
      crv: pubJwk.crv,
      x: pubJwk.x,
      y: pubJwk.y,
      use: "sig",
      alg: alg,
      kid: kid
    };
    console.log(`✅ EC key exported (${alg}, curve: ${namedCurve || pubJwk.crv})`);
    
  } else {
    console.error(`❌ Unsupported key type: ${pubJwk.kty}`);
    console.error("   Supported types: RSA, EC");
    process.exit(3);
  }
  
  // Verify NO private key components are present (security check)
  const privateComponents = ['d', 'p', 'q', 'dp', 'dq', 'qi'];
  const foundPrivate = privateComponents.filter(c => jwk.hasOwnProperty(c));
  
  if (foundPrivate.length > 0) {
    console.error(`❌ SECURITY ERROR: Private key components found in JWK: ${foundPrivate.join(', ')}`);
    console.error("   This should never happen. Aborting.");
    process.exit(4);
  }
  
  console.log("🔒 Security check passed: NO private key components in output");
  
  // Create JWKS structure (RFC 7517)
  const body = {
    keys: [jwk]
  };
  
  // Ensure output directory exists
  const outDir = path.dirname(outPath);
  if (!fs.existsSync(outDir)) {
    console.log("📁 Creating output directory:", outDir);
    fs.mkdirSync(outDir, { recursive: true });
  }
  
  // Write JWKS to file
  fs.writeFileSync(outPath, JSON.stringify(body, null, 2));
  
  console.log("");
  console.log("✅ SUCCESS!");
  console.log("   JWKS written to:", outPath);
  console.log("   Key ID (kid):", kid);
  console.log("   Algorithm:", jwk.alg);
  console.log("   Key type:", jwk.kty);
  console.log("");
  console.log("🌊 FOR THE COMMONS GOOD! 🌍🐟🚀");
  console.log("");
  console.log("Next steps:");
  console.log("  1. Serve this file at: https://your-domain/.well-known/jwks.json");
  console.log("  2. Keep private key secure (never commit to git!)");
  console.log("  3. Update Postman collection to use this JWKS endpoint");
  
} catch (error) {
  console.error("❌ Error:", error.message);
  console.error("");
  console.error("Troubleshooting:");
  console.error("  - Verify private key is in PEM format");
  console.error("  - Check file permissions");
  console.error("  - Ensure Node.js 18+ is installed");
  process.exit(5);
}
