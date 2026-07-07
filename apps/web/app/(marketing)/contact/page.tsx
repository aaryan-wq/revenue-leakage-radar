import { ContactPageClient } from "@/components/marketing/contact-page-client";
import { SiteFooter } from "@/components/site-footer";

const SUPPORT_EMAIL =
  process.env.SUPPORT_EMAIL ?? process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? "aaryan@paevo.co";

export default function ContactPage() {
  return (
    <>
      <ContactPageClient email={SUPPORT_EMAIL} />
      <SiteFooter />
    </>
  );
}
