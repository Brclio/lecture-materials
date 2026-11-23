// build.py prepends the lecture's path, byte length, SHA-256 and ordered parts.
async function fetchPart(assets, origin, path) {
  const response = await assets.fetch(origin + path);
  if (response.status !== 200 || !response.body) {
    throw new Error(`Lecture part unavailable (HTTP ${response.status})`);
  }
  return response.body;
}

async function writeLecture(first, assets, origin, writable) {
  try {
    await first.pipeTo(writable, { preventClose: true });
    for (const path of lecture.parts.slice(1)) {
      const body = await fetchPart(assets, origin, path);
      await body.pipeTo(writable, { preventClose: true });
    }
    await writable.close();
  } catch (error) {
    await writable.abort(error);
  }
}

export default {
  async fetch(request, env, context) {
    const url = new URL(request.url);
    let path;
    try {
      path = decodeURI(url.pathname);
    } catch {
      return new Response(null, { status: 404 });
    }
    if (path !== "/" && path !== "/index.html" && path !== lecture.path) {
      return new Response(null, { status: 404 });
    }
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response(null, { status: 405, headers: { Allow: "GET, HEAD" } });
    }

    const tag = `"${lecture.sha256}"`;
    const headers = new Headers({
      "Cache-Control": "public, no-cache, no-transform",
      "Content-Type": "text/html; charset=utf-8",
      ETag: "W/" + tag,
    });
    const validators = request.headers.get("If-None-Match") || "";
    if (validators.split(",").some(value => ["*", tag, "W/" + tag].includes(value.trim()))) {
      return new Response(null, { status: 304, headers });
    }
    if (request.method === "HEAD") {
      headers.set("Content-Length", String(lecture.size));
      return new Response(null, { headers });
    }

    const first = await fetchPart(env.ASSETS, url.origin, lecture.parts[0]);
    const stream = new FixedLengthStream(lecture.size);
    context.waitUntil(writeLecture(first, env.ASSETS, url.origin, stream.writable));
    return new Response(stream.readable, { headers });
  },
};
