import { PageTransition } from "@/components/ui/page-transition";

export default function AuditTemplate({ children }: { children: React.ReactNode }) {
  return <PageTransition>{children}</PageTransition>;
}
