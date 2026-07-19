import { create } from 'zustand';
import recommendStyling from '../../services/stylings/recommendStyling';
import type {
  GetDetailStylingResult,
  RecommendStylingResult,
  SaveStylingResult,
} from '../../types/stylings/Styling.types';
import saveStyling from '../../services/stylings/saveStyling';
import getDetailStyling from '../../services/stylings/getDetailStyling';

type StylingState = {
  isLoading: boolean;
  stylingLoading: boolean;
  errorMessage: string | null;

  stylingResult: RecommendStylingResult | null;
  stylingList: SaveStylingResult | null;
  detailStyling: GetDetailStylingResult | null;

  recommendStyling: (
    targetProductId: number
  ) => Promise<RecommendStylingResult | null>;
  saveStyling: (stylingId: number) => Promise<void>;
  fetchDetailStyling: (stylingId: number) => Promise<void>;
  reset: () => void;
};

export const useStylingStore = create<StylingState>((set) => ({
  isLoading: false,
  stylingLoading: false,
  errorMessage: null,

  stylingResult: null,
  stylingList: null,
  detailStyling: null,

  recommendStyling: async (targetProductId: number) => {
    set({ stylingLoading: true, errorMessage: null });

    try {
      const res = await recommendStyling(targetProductId);

      set({ stylingResult: res.result, stylingLoading: false });

      return res.result;
    } catch {
      set({
        stylingLoading: false,
        errorMessage: '스타일링 추천에 실패했습니다.',
      });

      return null;
    }
  },

  saveStyling: async (stylingId: number) => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await saveStyling(stylingId);

      set({ stylingList: res.result, isLoading: false });
    } catch {
      set({
        isLoading: false,
        errorMessage: '스타일링 저장에 실패했습니다.',
      });
    }
  },

  fetchDetailStyling: async (stylingId: number) => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await getDetailStyling(stylingId);

      set({
        detailStyling: res.result,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: '스타일링 상세 조회에 실패했습니다.',
      });
    }
  },

  reset: () =>
    set({
      isLoading: false,
      errorMessage: null,
      stylingResult: null,
    }),
}));
