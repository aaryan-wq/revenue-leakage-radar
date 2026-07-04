import { SignIn } from "@clerk/nextjs";

import { LegalConsent } from "@/components/legal/legal-consent";
import { Reveal } from "@/components/motion";
import { clerkAppearance } from "@/lib/clerk-appearance";

export default function SignInPage() {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-72px)] max-w-marketing items-center justify-center px-6 py-16 md:px-10">
      <Reveal className="w-full max-w-[28rem]">
        <SignIn fallbackRedirectUrl="/dashboard" appearance={clerkAppearance} />
        <LegalConsent action="signing in" className="mt-6 text-center" />
      </Reveal>
    </div>
  );
}
