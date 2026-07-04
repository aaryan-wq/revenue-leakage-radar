'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'motion/react'
import { Magnetic } from './motion'

const links = [
  { href: '/', label: 'Overview' },
  { href: '/upload', label: 'Upload' },
  { href: '/report', label: 'Report' },
  { href: '/workspace', label: 'Workspace' },
]

export function SiteNav() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50">
      <div className="absolute inset-0 -z-10 bg-background/70 backdrop-blur-xl" />
      <nav className="mx-auto flex h-16 max-w-[78rem] items-center justify-between px-6 md:px-10">
        <Link href="/" className="group flex items-center gap-2.5">
          <span className="relative flex h-2.5 w-2.5 items-center justify-center">
            <motion.span
              className="absolute inset-0 rounded-full bg-primary"
              animate={{ scale: [1, 1.9, 1], opacity: [0.5, 0, 0.5] }}
              transition={{ duration: 3.4, repeat: Infinity, ease: 'easeInOut' }}
            />
            <span className="h-2.5 w-2.5 rounded-full bg-primary" />
          </span>
          <span className="font-heading text-[1.05rem] tracking-tight text-foreground">
            Radar
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {links.map((l) => {
            const active =
              l.href === '/' ? pathname === '/' : pathname.startsWith(l.href)
            return (
              <Link
                key={l.href}
                href={l.href}
                className="relative px-3.5 py-2 text-[0.8rem] tracking-wide text-muted-foreground transition-colors hover:text-foreground"
              >
                {active && (
                  <motion.span
                    layoutId="nav-pill"
                    className="absolute inset-0 rounded-full bg-secondary"
                    transition={{ type: 'spring', stiffness: 380, damping: 32 }}
                  />
                )}
                <span
                  className={active ? 'relative text-foreground' : 'relative'}
                >
                  {l.label}
                </span>
              </Link>
            )
          })}
        </div>

        <Magnetic strength={0.25}>
          <Link
            href="/upload"
            className="inline-flex items-center rounded-full bg-primary px-4 py-2 text-[0.8rem] font-medium tracking-wide text-primary-foreground transition-shadow hover:shadow-[0_8px_30px_-8px] hover:shadow-primary/40"
          >
            Begin audit
          </Link>
        </Magnetic>
      </nav>
    </header>
  )
}
