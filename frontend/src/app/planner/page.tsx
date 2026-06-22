"use client";

import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { OccasionPicker } from "@/components/outfit/OccasionPicker";
import { WeekCalendar } from "@/components/planner/WeekCalendar";
import { usePlannerStore } from "@/store/plannerStore";
import { formatPercent, pluralize } from "@/utils/formatters";
import { CalendarDays } from "lucide-react";

export default function PlannerPage() {
  const {
    occasion, season, dayOverrides, plan, loading, error,
    setOccasion, setSeason, setDayOverride, generatePlan,
  } = usePlannerStore();

  return (
    <div>
      <PageHeader
        eyebrow="The Week Ahead"
        title="Weekly Planner"
        description="Seven days, zero repeats on consecutive tops or bottoms — color, style, and season balanced automatically."
      />

      <div className="px-6 md:px-10 py-6 border-b border-line">
        <div className="flex flex-col sm:flex-row sm:items-end gap-3 max-w-2xl">
          <div className="flex-1">
            <OccasionPicker
              occasion={occasion}
              season={season}
              onOccasionChange={setOccasion}
              onSeasonChange={setSeason}
            />
          </div>
          <Button onClick={generatePlan} disabled={loading} className="sm:w-auto">
            <span className="flex items-center gap-2">
              <CalendarDays size={14} />
              {loading ? "Planning…" : "Generate Week"}
            </span>
          </Button>
        </div>
      </div>

      <div className="px-6 md:px-10 py-8">
        {error && <p className="text-clay-light text-sm mb-4">{error}</p>}

        {!plan && !loading && !error && (
          <div className="text-center py-16 flex flex-col items-center gap-2">
            <CalendarDays size={28} strokeWidth={1} className="text-ink-faint" />
            <p className="text-sm text-ink-muted">Set a default occasion and season, then generate the week.</p>
          </div>
        )}

        {plan && (
          <div className="flex flex-col gap-6">
            <div className="grid grid-cols-3 gap-4 max-w-md">
              <Card>
                <CardBody className="text-center">
                  <p className="font-display text-2xl text-ink">{formatPercent(plan.coverage)}</p>
                  <p className="eyebrow mt-1">Coverage</p>
                </CardBody>
              </Card>
              <Card>
                <CardBody className="text-center">
                  <p className="font-display text-2xl text-ink">{plan.total_unique_tops}</p>
                  <p className="eyebrow mt-1">{pluralize(plan.total_unique_tops, "Top")}</p>
                </CardBody>
              </Card>
              <Card>
                <CardBody className="text-center">
                  <p className="font-display text-2xl text-ink">{plan.total_unique_bottoms}</p>
                  <p className="eyebrow mt-1">{pluralize(plan.total_unique_bottoms, "Bottom")}</p>
                </CardBody>
              </Card>
            </div>

            <WeekCalendar
              plan={plan}
              dayOverrides={dayOverrides}
              defaultOccasion={occasion}
              onOverrideChange={setDayOverride}
            />

            <div>
              <Button variant="outline" size="sm" onClick={generatePlan} disabled={loading}>
                {loading ? "Regenerating…" : "Regenerate with Overrides"}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
