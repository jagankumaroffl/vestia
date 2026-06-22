import { api } from "./api";
import type {
  ClothingItem,
  ClothingItemUpdate,
  WardrobeFilters,
} from "@/types/clothing";
import type { UploadAnalysisResult } from "@/types/api";

export const wardrobeApi = {
  async list(filters: WardrobeFilters = {}): Promise<ClothingItem[]> {
    const { data } = await api.get<ClothingItem[]>("/wardrobe", { params: filters });
    return data;
  },

  async get(id: number): Promise<ClothingItem> {
    const { data } = await api.get<ClothingItem>(`/wardrobe/${id}`);
    return data;
  },

  async update(id: number, updates: ClothingItemUpdate): Promise<ClothingItem> {
    const { data } = await api.patch<ClothingItem>(`/wardrobe/${id}`, updates);
    return data;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/wardrobe/${id}`);
  },

  async similar(id: number, k = 5): Promise<ClothingItem[]> {
    const { data } = await api.get<ClothingItem[]>(`/wardrobe/${id}/similar`, { params: { k } });
    return data;
  },

  async upload(
    file: File,
    overrides?: Partial<{ category: string; subcategory: string; style: string; season: string; tags: string }>
  ): Promise<UploadAnalysisResult> {
    const form = new FormData();
    form.append("file", file);
    if (overrides) {
      Object.entries(overrides).forEach(([key, value]) => {
        if (value) form.append(key, value);
      });
    }
    const { data } = await api.post<UploadAnalysisResult>("/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
};
