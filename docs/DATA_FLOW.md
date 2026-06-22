# Data Flow

## 1. Clothing Upload → Wardrobe

```mermaid
flowchart LR
    A["User selects photo<br/>(Upload page)"] --> B["POST /api/v1/upload<br/>multipart/form-data"]
    B --> C["validate_image()<br/>MIME type + size"]
    C --> D["save_upload()<br/>writes original + thumbnail<br/>to data/uploads/{user_id}/"]
    D --> E["analyze_image()"]
    E --> F["image_processor<br/>EXIF-correct, pad to 512×512"]
    F --> G["fashion_clip<br/>category, subcategory, style,<br/>pattern, season, gender, embedding"]
    F --> H["color_extractor<br/>K-Means → primary/secondary color"]
    G --> I["metadata_builder<br/>merges CV output"]
    H --> I
    I --> J{"User override<br/>fields provided?"}
    J -- yes --> K["merge overrides<br/>(user wins)"]
    J -- no --> L["use CV metadata as-is"]
    K --> M["ClothingRepository.create()<br/>→ clothing_items row"]
    L --> M
    I --> N["add_embedding()<br/>→ FAISS index"]
    I --> O{"confidence < 0.6?"}
    O -- yes --> P["needs_review=true<br/>shown in UI for correction"]
    O -- no --> Q["needs_review=false"]
    M --> R["201 UploadAnalysisResult"]
    N --> R
```

If `torch`/`transformers`/`faiss-cpu` aren't installed, `pipeline.py` and
`index_manager.py` degrade gracefully — the stub CV pipeline still returns
the full metadata shape (with `confidence=0.45`, always flagged for review),
and FAISS calls become no-ops.

## 2. Weekly Plan Generation

```mermaid
flowchart TB
    A["POST /api/v1/weekly-plan<br/>{occasion, season, day_overrides?}"] --> B["RecommendationService<br/>.generate_weekly_plan()"]
    B --> C["compute start_date<br/>(next Monday, or override)"]
    C --> D["for each weekday Mon→Sun"]
    D --> E["resolve occasion<br/>(day_overrides[day] ?? default)"]
    E --> F["OutfitService.generate_outfits(<br/>  count=15,<br/>  extra_recently_worn_ids=previous_day_items<br/>)"]
    F --> G["score & rank 15 candidates"]
    G --> H{"Tier 1: candidate exists with<br/>new top+bottom this week AND<br/>no repeat of yesterday?"}
    H -- yes --> I["choose it"]
    H -- no --> J{"Tier 2: candidate exists with<br/>no repeat of yesterday?"}
    J -- yes --> I
    J -- no --> K["Tier 3: best-scored<br/>candidate overall"]
    I --> L["record top/bottom ids in<br/>seen_top_ids / seen_bottom_ids<br/>(cumulative) and<br/>previous_day_items (consecutive)"]
    K --> L
    L --> D
    D -- "all 7 days done" --> M["WeeklyPlanResponse<br/>{days[], coverage,<br/>total_unique_tops, total_unique_bottoms}"]
```

The three-tier fallback is what makes "no consecutive repeats" a practical
guarantee rather than just a scoring nudge: Tier 1 maximizes weekly variety,
Tier 2 relaxes to "at least not identical to yesterday," and Tier 3 only
fires when the wardrobe is too small to satisfy either (e.g. a single top).

## 3. Outfit Scoring (per candidate)

```mermaid
flowchart LR
    Items["Candidate outfit<br/>(top, bottom, shoes, +optional outerwear/accessory)"] --> Color["color_rules<br/>score_color_combination()"]
    Items --> Style["style_rules<br/>score_style_combination()"]
    Items --> Occ["occasion_rules<br/>score_occasion_match()"]
    Items --> Season["season_rules<br/>score_season_match()"]
    Items --> Rep["repetition_rules<br/>score_repetition()"]

    Color -->|"×0.35"| Sum
    Style -->|"×0.30"| Sum
    Occ -->|"×0.20"| Sum
    Season -->|"×0.10"| Sum
    Rep -->|"×0.05"| Sum["total_score"]
```

Each sub-score is 0.0–1.0 and computed independently — see
[ARCHITECTURE.md](./ARCHITECTURE.md#layer-responsibilities) for the rule
tables behind each module.
