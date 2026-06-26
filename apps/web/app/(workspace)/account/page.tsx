import { AccountPageClient } from "@/components/account/account-page-client";

export default function AccountPage() {
  return (
    <div className="mx-auto max-w-container px-8 py-20">
      <header className="mb-16">
        <p className="text-overline uppercase text-gray-500">Settings</p>
        <h1 className="mt-4 text-h1 text-gray-900">Account</h1>
        <p className="mt-4 max-w-reading text-body text-gray-600">
          Manage your profile, security, and report entitlements.
        </p>
      </header>
      <AccountPageClient />
    </div>
  );
}
