/**
 * Cloudflare Pages Functions - API Reverse Proxy
 * 
 * Proxies requests to /api/* directly to your hosted backend (FastAPI / Render / Railway).
 * Set the `BACKEND_URL` environment variable in Cloudflare Pages (e.g. https://api.skillpulse.example.com).
 */
export async function onRequest(context) {
  const { request, env } = context;
  const backendUrl = env.BACKEND_URL;

  if (!backendUrl) {
    return new Response(
      JSON.stringify({
        error: "SkillPulse Cloudflare Pages Proxy: BACKEND_URL environment variable is not configured.",
        hint: "Add BACKEND_URL in Cloudflare Pages Dashboard -> Settings -> Environment Variables, or set VITE_API_BASE_URL during build."
      }),
      {
        status: 502,
        headers: { "Content-Type": "application/json" }
      }
    );
  }

  const url = new URL(request.url);
  const cleanBackend = backendUrl.replace(/\/+$/, '');
  const targetUrl = `${cleanBackend}${url.pathname}${url.search}`;

  const requestHeaders = new Headers(request.headers);
  try {
    requestHeaders.set("Host", new URL(cleanBackend).host);
  } catch (e) {
    // Keep original Host if parsing fails
  }

  const init = {
    method: request.method,
    headers: requestHeaders,
    redirect: "follow",
  };

  if (!["GET", "HEAD"].includes(request.method.toUpperCase())) {
    init.body = request.body;
    init.duplex = "half";
  }

  try {
    const response = await fetch(targetUrl, init);
    const responseHeaders = new Headers(response.headers);
    responseHeaders.set("Access-Control-Allow-Origin", "*");
    responseHeaders.set("Access-Control-Allow-Headers", "*");
    responseHeaders.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH");

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (err) {
    return new Response(
      JSON.stringify({
        error: "Failed to connect to backend server.",
        details: err.message
      }),
      {
        status: 504,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
}
