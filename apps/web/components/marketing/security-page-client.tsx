"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Lock, Server, Trash2 } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import { fadeUp, staggerContainer } from "@/lib/motion/variants";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";

const SUPPORT_EMAIL =
  process.env.SUPPORT_EMAIL ?? process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? "support@revenueleakageradar.com";

const SECTIONS: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: Lock,
    title: "Encryption",
    body: "All data is transmitted over HTTPS. PostgreSQL encryption at rest is managed by our cloud database provider.",
  },
  {
    icon: Trash2,
    title: "CSV Deletion",
    body: "Raw uploaded CSV files are stored only during active processing and automatically deleted after ingestion completes or the audit session expires.",
  },
  {
    icon: Server,
    title: "Infrastructure",
    body: "The application runs on industry-standard infrastructure: Next.js frontend, FastAPI backend, and PostgreSQL database. Secrets are stored in environment variables only.",
  },
];

export function SecurityPageClient() {
  const motionEnabled = useMotionEnabled();

  const enterProps = motionEnabled
    ? { variants: staggerContainer, initial: "hidden" as const, animate: "visible" as const }
    : { initial: false as const };

  const scrollProps = motionEnabled
    ? {
        variants: staggerContainer,
        initial: "hidden" as const,
        whileInView: "visible" as const,
        viewport: { once: true },
      }
    : { initial: false as const };

  const childVariants = motionEnabled ? fadeUp : undefined;

  return (
    <div className="mx-auto max-w-reading px-8 py-24">
      <motion.div {...enterProps}>
        <motion.p variants={childVariants} className="text-overline uppercase text-gray-500">
          Security
        </motion.p>
        <motion.h1 variants={childVariants} className="mt-4 text-h1 text-primary">
          Enterprise-grade data protection
        </motion.h1>
        <motion.p variants={childVariants} className="mt-4 text-body text-gray-600">
          Revenue Leakage Radar is built for finance teams handling sensitive billing data.
        </motion.p>
      </motion.div>

      <motion.div className="mt-16 space-y-8" {...scrollProps}>
        {SECTIONS.map((section) => (
          <motion.div key={section.title} variants={childVariants}>
            <GlassCard padding="md">
              <div className="flex items-center gap-3">
                <section.icon className="h-6 w-6 text-primary" strokeWidth={1.75} />
                <h2 className="text-h3 font-semibold text-gray-900">{section.title}</h2>
              </div>
              <p className="mt-4 text-body leading-relaxed text-gray-600">{section.body}</p>
            </GlassCard>
          </motion.div>
        ))}

        <motion.div variants={childVariants}>
          <GlassCard padding="md">
            <h2 className="text-h3 font-semibold text-gray-900">Retention Policy</h2>
            <p className="mt-4 text-body leading-relaxed text-gray-600">
              Canonical normalized records and audit metadata are retained to support purchased reports
              and dashboard history. Raw CSV uploads are never kept longer than required for processing.
            </p>
          </GlassCard>
        </motion.div>

        <motion.div variants={childVariants}>
          <GlassCard padding="md">
            <h2 className="text-h3 font-semibold text-gray-900">Contact</h2>
            <p className="mt-4 text-body text-gray-600">
              Security questions? Email{" "}
              <a href={`mailto:${SUPPORT_EMAIL}`} className="text-primary underline-offset-4 hover:underline">
                {SUPPORT_EMAIL}
              </a>{" "}
              or visit our{" "}
              <Link href="/contact" className="text-primary underline-offset-4 hover:underline">
                contact page
              </Link>
              .
            </p>
          </GlassCard>
        </motion.div>
      </motion.div>
    </div>
  );
}
