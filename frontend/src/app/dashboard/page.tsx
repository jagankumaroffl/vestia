"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { StatCard } from "@/components/dashboard/StatCard";
import { BreakdownBars } from "@/components/dashboard/BreakdownBars";
import { OutfitCard } from "@/components/outfit/OutfitCard";
import { statisticsApi, outfitApi } from "@/services/outfitApi";
import { pluralize } from "@/utils/formatters";
import type { WardrobeStats } from "@/types/api";
import type { Outfit } from "@/types/outfit";

export default function DashboardPage() {
  const [stats, setStats] = useState<WardrobeStats | null>(null);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [pick, setPick] = useState<Outfit | null>(null);
  const [pickError, setPickError] = useState<string | null>(null);
  const [loadingPick, setLoadingPick] = useState(false);

  useEffect(() => {
    statisticsApi.get().then(setStats).catch((err) => setStatsError(err.message));
  }, []);

  const loadTodaysPick = () => {
    setLoadingPick(true);
    setPickError(null);
    outfitApi
      .recommendations("casual", "all_season", 1)
      .then((outfits) => setPick(outfits[0] ?? null))
      .catch((err) => setPickError(err.message))
      .finally(() => setLoadingPick(false));
  };

  useEffect(() => {
    loadTodaysPick();
  }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Overview"
        title="Dashboard"
        description="Your wardrobe at a glance."
      />

      <div className="px-6 md:px-10 py-8 flex flex-col gap-8">
        {statsError && <p className="text-clay-light text-sm">{statsError}</p>}

        {stats && (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <StatCard value={stats.active_items} label={pluralize(stats.active_items, "Item")} />
              <StatCard value={stats.total_outfits_generated} label="Outfits Generated" />
              <StatCard value={stats.total_outfits_worn} label="Outfits Worn" />
              <StatCard value={Object.keys(stats.category_breakdown).length} label="Categories" />
            </div>

            <div className="grid sm:grid-cols-2 gap-5">
              <Card>
                <CardHeader>
                  <p className="eyebrow">By Category</p>
                </CardHeader>
                <CardBody>
                  <BreakdownBars data={stats.category_breakdown} />
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <p className="eyebrow">By Color</p>
                </CardHeader>
                <CardBody>
                  <BreakdownBars data={stats.color_breakdown} />
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <p className="eyebrow">By Style</p>
                </CardHeader>
                <CardBody>
                  <BreakdownBars data={stats.style_breakdown} />
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <p className="eyebrow">By Season</p>
                </CardHeader>
                <CardBody>
                  <BreakdownBars data={stats.season_breakdown} />
                </CardBody>
              </Card>
            </div>
          </>
        )}

        <div>
          <div className="flex items-center justify-between mb-3">
            <p className="eyebrow">Today&apos;s Pick</p>
            <Link href="/outfits">
              <Button variant="ghost" size="sm">More Options</Button>
            </Link>
          </div>

          {loadingPick && (
            <div className="h-64 bg-surface border border-line rounded-card animate-pulse" />
          )}

          {pickError && <p className="text-clay-light text-sm">{pickError}</p>}

          {!loadingPick && !pickError && !pick && (
            <Card>
              <CardBody className="text-center text-sm text-ink-muted py-10">
                Not enough wardrobe items yet for a recommendation.{" "}
                <Link href="/upload" className="text-gold hover:underline">Upload some clothes</Link> to get started.
              </CardBody>
            </Card>
          )}

          {pick && (
            <div className="max-w-md">
              <OutfitCard outfit={pick} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
