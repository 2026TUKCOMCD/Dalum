import { create } from "zustand";
import type { DupeSearchItem, StylingItem } from "../../types/me/Me.types";
import getDupeSearchList from "../../services/me/getDupeSearchList";
import getStylingList from "../../services/me/getStylingList";

type MeState = {
  isLoading: boolean;
  errorMessage: string | null;

  dupeSearchItem: DupeSearchItem[];
  stylingItem: StylingItem[];

  fetchDupeSaerchHistory: () => Promise<void>;
  fetchStylingList: () => Promise<void>;

  reset: () => void;
};

export const useMeStore = create<MeState>((set) => ({
  isLoading: false,
  errorMessage: null,

  dupeSearchItem: [],
  stylingItem: [],

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

  fetchStylingList: async () => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await getStylingList();

      set({
        stylingItem: res.result.stylings,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: "저장한 스타일링 목록 조회에 실패했습니다.",
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
