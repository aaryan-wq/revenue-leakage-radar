import Link from "next/link";
import { Mail } from "lucide-react";

import { ContactPageClient } from "@/components/marketing/contact-page-client";
import { SiteFooter } from "@/components/marketing/site-footer";

const SUPPORT_EMAIL =
  process.env.SUPPORT_EMAIL ?? process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? "support@revenueleakageradar.com";

export default function ContactPage() {
  return (
    <>
      <ContactPageClient email={SUPPORT_EMAIL} />
      <SiteFooter />
    </>
  );
}
