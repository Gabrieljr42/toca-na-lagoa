/**
 * Thin JSON wrapper around fetch. Services depend on this abstraction rather
 * than on fetch directly, so they can be exercised with a fake client.
 * `onUnauthorized` lets the app react to an expired session (e.g. show the
 * login page) without every service knowing about authentication.
 */

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export class HttpClient {
  constructor(fetchImpl = window.fetch.bind(window), { onUnauthorized = () => {} } = {}) {
    this.fetch = fetchImpl;
    this.onUnauthorized = onUnauthorized;
  }

  get(path, query = {}) {
    return this.request('GET', withQuery(path, query));
  }

  post(path, body) {
    return this.request('POST', path, body);
  }

  put(path, body) {
    return this.request('PUT', path, body);
  }

  patch(path, body) {
    return this.request('PATCH', path, body);
  }

  async request(method, path, body) {
    let response;
    try {
      response = await this.fetch(path, {
        method,
        headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
    } catch (error) {
      throw new ApiError('Sem conexão com o servidor. Tente de novo.', 0);
    }
    const payload = await response.json().catch(() => null);
    if (response.status === 401) this.onUnauthorized();
    if (!response.ok) {
      const detail = typeof payload?.detail === 'string' ? payload.detail : `Erro ${response.status}`;
      throw new ApiError(detail, response.status);
    }
    return payload;
  }
}

function withQuery(path, query) {
  const params = new URLSearchParams(query);
  const search = params.toString();
  return search ? `${path}?${search}` : path;
}
