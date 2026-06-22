"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, Shirt, Upload, Sparkles, CalendarDays } from "lucide-react";
import { cn } from "@/utils/cn";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutGrid },
  { href: "/wardrobe", label: "Wardrobe", icon: Shirt },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/outfits", label: "Outfit Generator", icon: Sparkles },
  { href: "/planner", label: "Weekly Planner", icon: CalendarDays },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-full md:w-56 md:min-h-screen border-b md:border-b-0 md:border-r border-line bg-surface">
      <div className="px-5 py-6 border-b border-line">
        <h1 className="font-display text-2xl text-ink tracking-wide">Vestia</h1>
        <p className="eyebrow mt-1">Personal Wardrobe</p>
      </div>
      <nav className="flex md:flex-col overflow-x-auto md:overflow-visible">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname?.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-5 py-3 text-sm whitespace-nowrap border-l-2 transition-colors",
                active
                  ? "border-gold text-ink bg-raised"
                  : "border-transparent text-ink-muted hover:text-ink hover:bg-raised"
              )}
            >
              <Icon size={16} strokeWidth={1.5} />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
