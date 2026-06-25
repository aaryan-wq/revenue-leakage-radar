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

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail ?? response.statusText;
  } catch {
    return response.statusText;
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { auditSession?: string } = {},
): Promise<T> {
  const { auditSession, headers: customHeaders, ...rest } = options;

  const headers = new Headers(customHeaders);
  if (auditSession) {
    headers.set("X-Audit-Session", auditSession);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers,
  });

  if (!response.ok) {
    const message = await parseError(response);
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}
