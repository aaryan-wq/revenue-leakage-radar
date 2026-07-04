const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface ApiFetchOptions extends RequestInit {
  auditSession?: string;
  authToken?: string | null;
  timeoutMs?: number;
}

const DEFAULT_TIMEOUT_MS = 15_000;

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail ?? response.statusText;
  } catch {
    return response.statusText;
  }
}

function buildHeaders(options: ApiFetchOptions): Headers {
  const { auditSession, authToken, headers: customHeaders } = options;
  const headers = new Headers(customHeaders);
  if (auditSession) {
    headers.set("X-Audit-Session", auditSession);
  }
  if (authToken) {
    headers.set("Authorization", `Bearer ${authToken}`);
  }
  return headers;
}

async function fetchWithTimeout(
  url: string,
  options: ApiFetchOptions,
): Promise<Response> {
  const {
    timeoutMs = DEFAULT_TIMEOUT_MS,
    signal: externalSignal,
    auditSession: _auditSession,
    authToken: _authToken,
    ...rest
  } = options;
  const controller = new AbortController();

  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  if (externalSignal) {
    if (externalSignal.aborted) {
      controller.abort();
    } else {
      externalSignal.addEventListener("abort", () => controller.abort(), { once: true });
    }
  }

  try {
    return await fetch(url, {
      ...rest,
      signal: controller.signal,
      headers: buildHeaders(options),
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(
        `The API at ${API_URL} did not respond in time. The backend may be hung or overloaded.`,
        0,
      );
    }
    throw new ApiError(
      `Cannot connect to the API at ${API_URL}. Confirm the backend is running, then open the app at http://localhost:3000 (not an IP address) if the browser blocks the request.`,
      0,
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const response = await fetchWithTimeout(`${API_URL}${path}`, options);

  if (!response.ok) {
    const message = await parseError(response);
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function apiDownload(
  path: string,
  options: ApiFetchOptions = {},
): Promise<Blob> {
  const response = await fetchWithTimeout(`${API_URL}${path}`, options);

  if (!response.ok) {
    const message = await parseError(response);
    throw new ApiError(message, response.status);
  }

  return response.blob();
}
