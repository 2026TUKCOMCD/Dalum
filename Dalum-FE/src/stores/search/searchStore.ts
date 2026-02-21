import { create } from "zustand";
import type {
  DupeProductsItem,
  SearchDupeProductsRequest,
} from "../../types/search/Search.types";
import searchDupeProducts from "../../services/search/searchDupeProduct";

type DupeSearchState = {
  isLoading: boolean;
  errorMessage: string | null;

  searchLogId: number | null;
  resultCount: number;
  products: DupeProductsItem[];

  searchDupe: (req: SearchDupeProductsRequest) => Promise<void>;
  reset: () => void;
};

export const useSearchStore = create<DupeSearchState>((set) => ({
  isLoading: false,
  errorMessage: null,

  searchLogId: null,
  resultCount: 0,
  products: [],

  searchDupe: async (req) => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await searchDupeProducts(req);

      set({
        searchLogId: res.result.searchLogId,
        resultCount: res.result.resultCount,
        products: res.result.products,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: "듀프 제품 검색에 실패했어요.",
      });
    }
  },

  reset: () =>
    set({
      isLoading: false,
      errorMessage: null,
      searchLogId: null,
      resultCount: 0,
      products: [],
    }),
}));
