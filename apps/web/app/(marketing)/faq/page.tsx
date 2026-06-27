"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

import { Reveal } from "@/components/motion";
import { SiteFooter } from "@/components/site-footer";
import { HairlineCard } from "@/components/ui/hairline-card";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";

const FAQ_ITEMS = [
  {
    q: "How secure are my uploads?",
    a: "All uploads are encrypted in transit (HTTPS/TLS). Raw CSV files are processed temporarily and automatically deleted after ingestion. Free audits do not persist raw uploads beyond what is required to produce your summary.",
  },
  {
    q: "What billing systems work?",
    a: "Any system that exports CSV. We commonly see Stripe, Chargebee, Maxio, Zuora, HubSpot, and Salesforce exports. Upload invoice line items and a price catalog to begin.",
  },
  {
    q: "How accurate are findings?",
    a: "Every finding is produced by deterministic verification rules — not AI. Each includes a confidence score based on data coverage and evidence quality. AI assists with narratives only.",
  },
  {
    q: "How long does an audit take?",
    a: "Most audits complete in a few minutes. You will see real-time progress during validation and verification.",
  },
  {
    q: "Can I upload multiple exports?",
    a: "Yes. Add subscriptions, invoices, customers, and coupons to improve coverage and unlock additional verification rules.",
  },
  {
    q: "Do you store my data?",
    a: "Raw CSVs are deleted after processing. Normalized audit results are retained only for purchased reports and your workspace history. You retain full ownership of your data.",
  },
  {
    q: "Do I need an account for a free audit?",
    a: "No. Upload and receive a free summary without signing in. An account is only required when purchasing a detailed report or saving results to your workspace.",
  },
  {
    q: "What is included in the free summary vs. the detailed report?",
    a: "The free summary shows estimated recoverable ARR, top categories, coverage, and confidence — with customer names and evidence blurred. The detailed report unlocks full evidence, remediation steps, and exports.",
  },
  {
    q: "What is the ROI on a $999 detailed report?",
    a: "Most finance teams recover more than the report cost in the first finding. Annual membership delivers the strongest ROI for teams running quarterly audits.",
  },
];

function FaqItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false);
  const motionEnabled = useMotionEnabled();

  return (
    <div className="border-b border-line last:border-0">
      <button
        type="button"
        className="focus-ring flex w-full items-center justify-between py-5 text-left"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <span className="font-medium text-foreground">{question}</span>
        <ChevronDown
          className={`h-5 w-5 shrink-0 text-muted-foreground transition-transform duration-normal ${open ? "rotate-180" : ""}`}
          strokeWidth={1.75}
        />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.p
            initial={motionEnabled ? { opacity: 0, height: 0 } : false}
            animate={{ opacity: 1, height: "auto" }}
            exit={motionEnabled ? { opacity: 0, height: 0 } : { opacity: 0 }}
            transition={{ duration: motionEnabled ? 0.2 : 0.15 }}
            className="overflow-hidden pb-5 leading-relaxed text-muted-foreground"
          >
            {answer}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function FaqPage() {
  return (
    <>
      <div className="mx-auto max-w-reading px-6 py-28 md:px-10">
        <Reveal>
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">FAQ</p>
          <h1 className="mt-4 font-heading text-[clamp(2rem,4.5vw,3.4rem)] leading-[1.02] tracking-tight text-balance">
            Frequently Asked Questions
          </h1>
          <p className="mt-4 leading-relaxed text-muted-foreground">
            Common questions about uploads, pricing, and data handling.
          </p>
        </Reveal>

        <Reveal delay={0.1} className="mt-12">
          <HairlineCard padding="md">
            {FAQ_ITEMS.map((item) => (
              <FaqItem key={item.q} question={item.q} answer={item.a} />
            ))}
          </HairlineCard>
        </Reveal>
      </div>
      <SiteFooter />
    </>
  );
}
