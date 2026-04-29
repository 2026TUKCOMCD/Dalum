import { create } from 'zustand';
import type {
  DupeProductsItem,
  SearchDupeProductsData,
  SearchDupeProductsRequest,
} from '../../types/search/Search.types';
import searchDupeProducts from '../../services/search/searchDupeProduct';

type DupeSearchState = {
  isLoading: boolean;
  errorMessage: string | null;

  searchLogId: number | null;
  resultCount: number;
  productsList: SearchDupeProductsData | null;
  products: DupeProductsItem[];

  searchDupe: (req: SearchDupeProductsRequest) => Promise<number>;
  reset: () => void;
};

export const useSearchStore = create<DupeSearchState>((set) => ({
  isLoading: false,
  errorMessage: null,

  searchLogId: null,
  resultCount: 0,
  productsList: null,
  products: [],

  searchDupe: async (req) => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await searchDupeProducts(req);
      const id = res.result.searchLogId;

      set({
        searchLogId: id,
        productsList: res.result,
        resultCount: res.result.resultCount,
        products: res.result.products,
        isLoading: false,
      });

      return id;
    } catch {
      set({
        isLoading: false,
        errorMessage: '듀프 제품 검색에 실패했어요.',
      });
      throw new Error('searchDupe failed');
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
