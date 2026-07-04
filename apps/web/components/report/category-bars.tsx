"use client";

import { motion } from "framer-motion";

import { glide } from "@/components/motion";
import { formatCurrency, type OpportunityBreakdownItem } from "@rlr/shared";

interface CategoryBarsProps {
  items: OpportunityBreakdownItem[];
}

export function CategoryBars({ items }: CategoryBarsProps) {
  if (items.length === 0) {
    return (
      <p className="text-sm leading-relaxed text-muted-foreground">
        No category breakdown available for this report.
      </p>
    );
  }

  const max = Math.max(...items.map((item) => parseFloat(item.arr) || 0), 1);

  return (
    <div className="space-y-7">
      {items.map((item, index) => {
        const amount = parseFloat(item.arr) || 0;
        return (
          <div key={item.category}>
            <div className="mb-2.5 flex items-baseline justify-between">
              <span className="text-[0.95rem] text-foreground">{item.label}</span>
              <span className="font-heading text-lg tracking-tight tnum">
                {formatCurrency(item.arr)}
              </span>
            </div>
            <div className="h-px w-full bg-line">
              <motion.div
                className="h-px bg-primary"
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: amount / max }}
                viewport={{ once: true }}
                transition={{ duration: 1.2, ease: glide, delay: index * 0.1 }}
                style={{ originX: 0 }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
