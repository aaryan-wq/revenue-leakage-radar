import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isPublicRoute = createRouteMatcher([
  "/",
  "/upload(.*)",
  "/validation(.*)",
  "/analysis(.*)",
  "/summary(.*)",
  "/report(.*)",
  "/findings(.*)",
  "/pricing",
  "/security",
  "/faq",
  "/contact",
  "/privacy",
  "/terms",
  "/checkout/success",
  "/checkout/cancel",
  "/sign-in(.*)",
  "/sign-up(.*)",
]);

const clerkConfigured = Boolean(
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
    !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes("your_key_here"),
);

export default clerkMiddleware(async (auth, request) => {
  if (!clerkConfigured) {
    return;
  }
  if (!isPublicRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
    "/__clerk/:path*",
  ],
};
