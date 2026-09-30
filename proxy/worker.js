// Cloudflare Worker that forwards AI Chef requests to Anthropic.
//
// The Claude API key is stored as the Worker secret ANTHROPIC_API_KEY
// (set with `npx wrangler secret put ANTHROPIC_API_KEY`). It never appears
// in the website's code or in this repository.

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MAX_TOKENS_CAP = 4096;

function isAllowedOrigin(origin, env) {
  if (!origin) return false;
  const allowed = (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (allowed.includes(origin)) return true;
  // Local development: a dev server on localhost, or index.html opened straight from disk.
  if (/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) return true;
  if (origin === "null") return true;
  return false;
}

function corsHeaders(origin) {
  return {
    "access-control-allow-origin": origin,
    "access-control-allow-methods": "POST, OPTIONS",
    "access-control-allow-headers": "content-type, x-api-key",
    "access-control-max-age": "86400",
    "vary": "origin",
  };
}

function jsonResponse(obj, status, extraHeaders) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { ...extraHeaders, "content-type": "application/json" },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("origin") || "";
    if (!isAllowedOrigin(origin, env)) {
      return new Response("Forbidden", { status: 403 });
    }
    const cors = corsHeaders(origin);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405, headers: cors });
    }

    let body;
    try {
      body = await request.json();
    } catch (e) {
      return jsonResponse({ error: { message: "Invalid JSON body" } }, 400, cors);
    }
    if (typeof body.model !== "string" || !body.model.startsWith("claude-")) {
      return jsonResponse({ error: { message: "Model not allowed" } }, 400, cors);
    }
    body.max_tokens = Math.min(Number(body.max_tokens) || 1024, MAX_TOKENS_CAP);
    body.stream = false;

    // A key the visitor saved in the site's Settings overrides the built-in one.
    const apiKey = request.headers.get("x-api-key") || env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return jsonResponse({ error: { message: "No API key configured on the proxy" } }, 500, cors);
    }

    const upstream = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify(body),
    });

    return new Response(upstream.body, {
      status: upstream.status,
      headers: { ...cors, "content-type": upstream.headers.get("content-type") || "application/json" },
    });
  },
};
