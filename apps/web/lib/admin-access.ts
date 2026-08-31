const DEFAULT_ADMIN_EMAILS = "aaryan@paevo.co";

function parseAdminEmails(raw: string | undefined): string[] {
  const value = raw ?? DEFAULT_ADMIN_EMAILS;
  return value
    .split(",")
    .map((email) => email.trim().toLowerCase())
    .filter(Boolean);
}

export function getAdminEmailAllowlist(): string[] {
  return parseAdminEmails(process.env.NEXT_PUBLIC_ADMIN_EMAILS);
}

interface ClerkLikeUser {
  primaryEmailAddress?: { emailAddress?: string | null } | null;
  emailAddresses?: Array<{ emailAddress?: string | null }>;
  publicMetadata?: Record<string, unknown>;
}

export function isAdminUser(user: ClerkLikeUser | null | undefined): boolean {
  if (!user) return false;

  const role = user.publicMetadata?.role;
  if (role === "admin") return true;

  const primary =
    user.primaryEmailAddress?.emailAddress ??
    user.emailAddresses?.[0]?.emailAddress ??
    null;

  if (!primary) return false;
  return getAdminEmailAllowlist().includes(primary.trim().toLowerCase());
}
