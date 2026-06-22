import { api } from "./api";
import type { WeeklyPlanRequest, WeeklyPlanResponse } from "@/types/api";

export const plannerApi = {
  async generateWeeklyPlan(req: WeeklyPlanRequest): Promise<WeeklyPlanResponse> {
    const { data } = await api.post<WeeklyPlanResponse>("/weekly-plan", req);
    return data;
  },
};
