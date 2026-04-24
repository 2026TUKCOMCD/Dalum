import { create } from 'zustand';
import toggleLike from '../../services/products/toggleLike';

type ProductState = {
  isLoadingById: Record<number, boolean>;
  errorMessage: string | null;

  likeStatusById: Record<number, boolean>;

  updateLikes: (items: { id: number; isLiked: boolean }[]) => void;

  setLikeStatus: (productId: number, isLiked: boolean) => void;

  toggleLikeStatus: (productId: number) => Promise<void>;
  reset: () => void;
};

export const useProductStore = create<ProductState>((set, get) => ({
  isLoadingById: {},
  errorMessage: null,

  likeStatusById: {},

  updateLikes: (items) =>
    set((state) => {
      const next = { ...state.likeStatusById };
      for (const it of items) next[it.id] = it.isLiked;
      return { likeStatusById: next };
    }),

  setLikeStatus: (productId, isLiked) =>
    set((state) => ({
      likeStatusById: { ...state.likeStatusById, [productId]: isLiked },
    })),

  toggleLikeStatus: async (productId: number) => {
    const prev = get().likeStatusById[productId] ?? false;

    set((state) => ({
      errorMessage: null,
      isLoadingById: { ...state.isLoadingById, [productId]: true },
      likeStatusById: { ...state.likeStatusById, [productId]: !prev },
    }));

    try {
      const res = await toggleLike(productId);

      set((state) => ({
        isLoadingById: { ...state.isLoadingById, [productId]: false },
        likeStatusById: {
          ...state.likeStatusById,
          [productId]: res.result.isLiked,
        },
      }));
    } catch {
      set((state) => ({
        isLoadingById: { ...state.isLoadingById, [productId]: false },
        likeStatusById: { ...state.likeStatusById, [productId]: prev },
        errorMessage: '좋아요 상태 변경에 실패했어요.',
      }));
    }
  },

  reset: () =>
    set({
      isLoadingById: {},
      errorMessage: null,
      likeStatusById: {},
    }),
}));
