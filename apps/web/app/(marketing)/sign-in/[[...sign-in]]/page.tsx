import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-72px)] max-w-container items-center justify-center px-8 py-16">
      <SignIn fallbackRedirectUrl="/dashboard" />
    </div>
  );
}
