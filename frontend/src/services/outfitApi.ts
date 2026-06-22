import { api } from "./api";
import type { GenerateOutfitRequest, Outfit } from "@/types/outfit";
import type { WardrobeStats } from "@/types/api";

export const outfitApi = {
  async generate(req: GenerateOutfitRequest): Promise<Outfit[]> {
    const { data } = await api.post<Outfit[]>("/generate-outfit", req);
    return data;
  },

  async recommendations(occasion: string, season: string, count = 5): Promise<Outfit[]> {
    const { data } = await api.get<Outfit[]>("/recommendations", {
      params: { occasion, season, count },
    });
    return data;
  },

  async list(params: { occasion?: string; season?: string; skip?: number; limit?: number } = {}): Promise<Outfit[]> {
    const { data } = await api.get<Outfit[]>("/outfits", { params });
    return data;
  },

  async get(id: number): Promise<Outfit> {
    const { data } = await api.get<Outfit>(`/outfits/${id}`);
    return data;
  },

  async markWorn(id: number, payload: { worn_date?: string; occasion?: string; notes?: string } = {}): Promise<void> {
    await api.post(`/outfits/${id}/worn`, { outfit_id: id, ...payload });
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/outfits/${id}`);
  },
};

export const statisticsApi = {
  async get(): Promise<WardrobeStats> {
    const { data } = await api.get<WardrobeStats>("/statistics");
    return data;
  },
};
