"use client";

import { useRef, useState } from "react";
import { Upload as UploadIcon, ImagePlus, CheckCircle2, AlertTriangle } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { ColorSwatch } from "@/components/ui/ColorSwatch";
import { wardrobeApi } from "@/services/wardrobeApi";
import { CATEGORIES, STYLES, SEASONS, PATTERNS, type ClothingItemUpdate } from "@/types/clothing";
import { titleCase } from "@/utils/colorUtils";
import type { UploadAnalysisResult } from "@/types/api";

const FIELD_CLASS =
  "w-full bg-canvas border border-line rounded-card px-3 py-2 text-sm text-ink focus:border-gold transition-colors";

export default function UploadPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadAnalysisResult | null>(null);
  const [corrections, setCorrections] = useState<ClothingItemUpdate>({});

  const handleFile = (f: File) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setCorrections({});
    setSaved(false);
    setError(null);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await wardrobeApi.upload(file);
      setResult(res);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(false);
    }
  };

  const handleSaveCorrections = async () => {
    if (!result || Object.keys(corrections).length === 0) return;
    setSaving(true);
    try {
      await wardrobeApi.update(result.clothing_item_id, corrections);
      setSaved(true);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setCorrections({});
    setSaved(false);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const current = result ? { ...result, ...corrections } : null;

  return (
    <div>
      <PageHeader
        eyebrow="Add to Closet"
        title="Upload"
        description="One garment per photo. Vestia identifies category, color, pattern, style, and season automatically."
      />

      <div className="px-6 md:px-10 py-8 max-w-3xl">
        {!preview ? (
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className="border border-dashed border-line rounded-card aspect-[3/2] flex flex-col items-center justify-center gap-3 cursor-pointer hover:border-ink-faint transition-colors"
          >
            <ImagePlus size={32} strokeWidth={1} className="text-ink-faint" />
            <p className="text-sm text-ink-muted">Drag a photo here, or click to browse</p>
            <p className="eyebrow">JPEG · PNG · WebP</p>
            <input
              ref={inputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFile(f);
              }}
            />
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 gap-6">
            <div className="aspect-square bg-surface border border-line rounded-card overflow-hidden">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={preview} alt="Preview" className="w-full h-full object-cover" />
            </div>

            <div className="flex flex-col gap-4">
              {!result ? (
                <Card>
                  <CardBody className="flex flex-col gap-4">
                    <p className="text-sm text-ink-muted">
                      Ready to analyze. Vestia will detect category, colors, pattern, style, and season.
                    </p>
                    <div className="flex gap-2">
                      <Button onClick={handleAnalyze} disabled={uploading}>
                        {uploading ? "Analyzing…" : "Analyze & Save"}
                      </Button>
                      <Button variant="ghost" onClick={handleReset} disabled={uploading}>
                        Choose Different Photo
                      </Button>
                    </div>
                  </CardBody>
                </Card>
              ) : (
                <Card>
                  <CardBody className="flex flex-col gap-4">
                    <div className="flex items-center gap-2">
                      {result.needs_review ? (
                        <Badge tone="clay"><AlertTriangle size={11} /> Needs Review</Badge>
                      ) : (
                        <Badge tone="sage"><CheckCircle2 size={11} /> Saved to Wardrobe</Badge>
                      )}
                      <Badge>{Math.round(result.confidence * 100)}% confidence</Badge>
                    </div>

                    <div>
                      <label className="eyebrow block mb-1.5">Category</label>
                      <select
                        className={FIELD_CLASS}
                        value={current?.category}
                        onChange={(e) => setCorrections({ ...corrections, category: e.target.value as any })}
                      >
                        {CATEGORIES.map((c) => (
                          <option key={c} value={c}>{titleCase(c)}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="eyebrow block mb-1.5">Subcategory</label>
                      <input
                        className={FIELD_CLASS}
                        value={current?.subcategory ?? ""}
                        onChange={(e) => setCorrections({ ...corrections, subcategory: e.target.value })}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="eyebrow block mb-1.5">Style</label>
                        <select
                          className={FIELD_CLASS}
                          value={current?.style}
                          onChange={(e) => setCorrections({ ...corrections, style: e.target.value as any })}
                        >
                          {STYLES.map((s) => (
                            <option key={s} value={s}>{titleCase(s)}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="eyebrow block mb-1.5">Season</label>
                        <select
                          className={FIELD_CLASS}
                          value={current?.season}
                          onChange={(e) => setCorrections({ ...corrections, season: e.target.value as any })}
                        >
                          {SEASONS.map((s) => (
                            <option key={s} value={s}>{titleCase(s)}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="eyebrow block mb-1.5">Pattern</label>
                      <select
                        className={FIELD_CLASS}
                        value={current?.pattern}
                        onChange={(e) => setCorrections({ ...corrections, pattern: e.target.value as any })}
                      >
                        {PATTERNS.map((p) => (
                          <option key={p} value={p}>{titleCase(p)}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="eyebrow block mb-1.5">Detected Colors</label>
                      <div className="flex items-center gap-2">
                        <ColorSwatch name={result.primary_color} size={18} />
                        <span className="text-sm text-ink">{titleCase(result.primary_color)}</span>
                        {result.secondary_color && (
                          <>
                            <span className="text-ink-faint">/</span>
                            <ColorSwatch name={result.secondary_color} size={18} />
                            <span className="text-sm text-ink">{titleCase(result.secondary_color)}</span>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2 pt-2">
                      <Button
                        onClick={handleSaveCorrections}
                        disabled={saving || Object.keys(corrections).length === 0}
                      >
                        {saving ? "Saving…" : saved ? "Saved" : "Save Corrections"}
                      </Button>
                      <Button variant="ghost" onClick={handleReset}>
                        Upload Another
                      </Button>
                    </div>
                  </CardBody>
                </Card>
              )}

              {error && <p className="text-clay-light text-sm">{error}</p>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
