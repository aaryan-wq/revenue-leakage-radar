function resolveApiUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (url) {
    return url;
  }
  if (process.env.NODE_ENV === "production") {
    throw new Error("NEXT_PUBLIC_API_URL must be set in production.");
  }
  return "http://localhost:8000";
}

export const API_URL = resolveApiUrl();
