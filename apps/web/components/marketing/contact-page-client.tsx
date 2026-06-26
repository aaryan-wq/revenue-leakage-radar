"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Mail } from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import { fadeUp, staggerContainer } from "@/lib/motion/variants";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";

interface ContactPageClientProps {
  email: string;
}

export function ContactPageClient({ email }: ContactPageClientProps) {
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
    <div className="mx-auto max-w-reading px-8 py-24">
      <motion.div {...enterProps}>
        <motion.p variants={childVariants} className="text-overline uppercase text-gray-500">
          Contact
        </motion.p>
        <motion.h1 variants={childVariants} className="mt-4 text-h1 text-primary">
          We are here to help
        </motion.h1>
        <motion.p variants={childVariants} className="mt-4 text-body text-gray-600">
          Questions about your audit, billing, or security? Reach out to our team.
        </motion.p>
      </motion.div>

      <motion.div className="mt-12" {...scrollProps}>
        <GlassCard padding="lg" className="text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-surface-glass-subtle">
            <Mail className="h-7 w-7 text-primary" strokeWidth={1.75} />
          </div>
          <h2 className="mt-6 text-h3 font-semibold text-gray-900">Email Support</h2>
          <p className="mt-3 text-body text-gray-600">
            For billing, technical, or security inquiries, email our team.
          </p>
          <a
            href={`mailto:${email}`}
            className="mt-8 inline-flex h-12 items-center rounded-button bg-primary px-8 text-body font-medium text-white transition-all hover:brightness-[1.04] active:scale-[0.98]"
          >
            {email}
          </a>
        </GlassCard>
      </motion.div>

      <p className="mt-8 text-center text-body text-gray-500">
        Looking for quick answers? Visit our{" "}
        <Link href="/faq" className="text-primary underline-offset-4 hover:underline">
          FAQ
        </Link>
        .
      </p>
    </div>
  );
}
