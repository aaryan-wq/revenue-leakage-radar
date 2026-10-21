import { PageTransition } from "@/components/ui/page-transition";

export default function MarketingTemplate({ children }: { children: React.ReactNode }) {
  return <PageTransition>{children}</PageTransition>;
}
