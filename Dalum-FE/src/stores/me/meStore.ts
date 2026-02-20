import { create } from "zustand";
import type { DupeSearchItem } from "../../types/me/Me.types";
import getDupeSearchList from "../../services/me/getDupeSearchList";

type MeState = {
  isLoading: boolean;
  errorMessage: string | null;

  dupeSearchItem: DupeSearchItem[];

  fetchDupeSaerchHistory: () => Promise<void>;
  reset: () => void;
};

export const useMeStore = create<MeState>((set) => ({
  isLoading: false,
  errorMessage: null,

  dupeSearchItem: [],

  fetchDupeSaerchHistory: async () => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await getDupeSearchList();

      set({
        dupeSearchItem: res.result.searchLogs,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: "듀프 제품 검색 기록 조회에 실패했습니다.",
      });
    }
  },

  reset: () =>
    set({
      isLoading: false,
      errorMessage: null,
      dupeSearchItem: [],
    }),
}));
