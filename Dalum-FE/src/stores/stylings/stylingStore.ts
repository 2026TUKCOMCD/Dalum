import { create } from 'zustand';
import recommendStyling from '../../services/stylings/recommendStyling';
import type { RecommendStylingResult } from '../../types/stylings/Styling.types';

type StylingState = {
  isLoading: boolean;
  errorMessage: string | null;

  stylingResult: RecommendStylingResult | null;

  recommendStyling: (targetProductId: number) => Promise<void>;
  reset: () => void;
};

export const useStylingStore = create<StylingState>((set) => ({
  isLoading: false,
  errorMessage: null,

  stylingResult: null,

  recommendStyling: async (targetProductId: number) => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await recommendStyling(targetProductId);

      set({ stylingResult: res.result, isLoading: false });
    } catch {
      set({
        isLoading: false,
        errorMessage: '스타일링 추천에 실패했습니다.',
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
