"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

import { SiteFooter } from "@/components/marketing/site-footer";
import { GlassCard } from "@/components/ui/glass-card";
import { fadeUp, staggerContainer } from "@/lib/motion/variants";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";

const FAQ_ITEMS = [
  {
    q: "Do I need an account to run a free scan?",
    a: "No. You can upload billing CSVs and receive a free Revenue Verification Summary without creating an account. Sign in is only required when purchasing a detailed report.",
  },
  {
    q: "What billing platforms are supported?",
    a: "We support CSV exports from Stripe, Chargebee, Maxio, Zuora, and generic billing exports. Upload invoice line items and a price catalog to begin; additional files unlock more rules.",
  },
  {
    q: "What files do I need to upload?",
    a: "Required (Tier 0): invoice_line_items.csv and prices.csv (or price_catalog.csv). Strongly recommended (Tier 1): subscriptions, invoices, and customers. Optional: coupons and CRM exports for discount and contract rules.",
  },
  {
    q: "How long does verification take?",
    a: "Most scans complete within a few minutes depending on data volume. You will see real-time progress during analysis.",
  },
  {
    q: "What is included in the free summary?",
    a: "Estimated recoverable ARR, opportunity breakdown by category, verification checklist status, and a blurred preview of top findings.",
  },
  {
    q: "What is included in the detailed report?",
    a: "Customer-level findings, invoice-level evidence, executive narrative, remediation guidance, and PDF/CSV exports.",
  },
  {
    q: "How does annual membership work?",
    a: "Annual membership includes 12 detailed report credits per year. Credits are consumed when you unlock a specific audit report.",
  },
  {
    q: "When are my CSV files deleted?",
    a: "Raw uploaded CSV files are automatically deleted after processing completes. See our Security page for details.",
  },
  {
    q: "Does AI make financial decisions?",
    a: "No. Revenue leakage detection, ARR calculations, and confidence scoring are fully deterministic. AI assists with column mapping and narrative generation only.",
  },
  {
    q: "What payment methods are accepted?",
    a: "Payments are processed securely through Stripe Checkout. Major credit cards are accepted.",
  },
  {
    q: "Can I get a receipt?",
    a: "Yes. Receipts are available through Stripe after purchase and listed on your Billing page.",
  },
  {
    q: "What is your refund policy?",
    a: "Contact support within 7 days of purchase if you believe there was a processing error. We review refund requests on a case-by-case basis.",
  },
];

function FaqItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false);
  const motionEnabled = useMotionEnabled();

  return (
    <div className="border-b border-border last:border-0">
      <button
        type="button"
        className="focus-ring flex w-full items-center justify-between py-5 text-left"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <span className="text-body font-medium text-gray-900">{question}</span>
        <ChevronDown
          className={`h-5 w-5 shrink-0 text-gray-400 transition-transform duration-normal ${open ? "rotate-180" : ""}`}
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
            className="overflow-hidden pb-5 text-body text-gray-600"
          >
            {answer}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function FaqPage() {
  const motionEnabled = useMotionEnabled();

  const enterProps = motionEnabled
    ? { variants: staggerContainer, initial: "hidden" as const, animate: "visible" as const }
    : { initial: false as const };

  const scrollProps = motionEnabled
    ? {
        variants: fadeUp,
        initial: "hidden" as const,
        whileInView: "visible" as const,
        viewport: { once: true },
      }
    : { initial: false as const };

  const childVariants = motionEnabled ? fadeUp : undefined;

  return (
    <>
      <div className="mx-auto max-w-reading px-8 py-24">
        <motion.div {...enterProps}>
          <motion.p variants={childVariants} className="text-overline uppercase text-gray-500">
            FAQ
          </motion.p>
          <motion.h1 variants={childVariants} className="mt-4 text-h1 text-primary">
            Frequently Asked Questions
          </motion.h1>
          <motion.p variants={childVariants} className="mt-4 text-body text-gray-600">
            Common questions about uploads, pricing, and data handling.
          </motion.p>
        </motion.div>
        <motion.div className="mt-12" {...scrollProps}>
          <GlassCard padding="md">
            {FAQ_ITEMS.map((item) => (
              <FaqItem key={item.q} question={item.q} answer={item.a} />
            ))}
          </GlassCard>
        </motion.div>
      </div>
      <SiteFooter />
    </>
  );
}
