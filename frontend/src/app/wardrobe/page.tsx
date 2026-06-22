import { PageHeader } from "@/components/layout/PageHeader";
import { FilterBar } from "@/components/wardrobe/FilterBar";
import { ClothingGrid } from "@/components/wardrobe/ClothingGrid";

export default function WardrobePage() {
  return (
    <div>
      <PageHeader
        eyebrow="Closet"
        title="Wardrobe"
        description="Every piece you've catalogued, organized and ready to style."
      />
      <FilterBar />
      <ClothingGrid />
    </div>
  );
}
