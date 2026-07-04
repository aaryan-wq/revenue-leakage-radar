import { SignUp } from "@clerk/nextjs";

import { LegalConsent } from "@/components/legal/legal-consent";
import { Reveal } from "@/components/motion";
import { clerkAppearance } from "@/lib/clerk-appearance";

export default function SignUpPage() {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-72px)] max-w-marketing items-center justify-center px-6 py-16 md:px-10">
      <Reveal className="w-full max-w-[28rem]">
        <SignUp fallbackRedirectUrl="/dashboard" appearance={clerkAppearance} />
        <LegalConsent action="creating an account" className="mt-6 text-center" />
      </Reveal>
    </div>
  );
}
