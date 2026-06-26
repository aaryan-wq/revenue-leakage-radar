import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-72px)] max-w-container items-center justify-center px-8 py-16">
      <SignUp fallbackRedirectUrl="/dashboard" />
    </div>
  );
}
