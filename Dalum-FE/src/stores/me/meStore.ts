import { create } from 'zustand';
import type {
  DetailDupeSearchItem,
  DetailDupeSearchList,
  DupeSearchItem,
  LikeItem,
  StylingItem,
} from '../../types/me/Me.types';
import getDupeSearchList from '../../services/me/getDupeSearchList';
import getStylingList from '../../services/me/getStylingList';
import getLikeList from '../../services/me/getLikeList';
import getDetailDupeSearch from '../../services/me/getDetailDupeSearch';

type MeState = {
  isLoading: boolean;
  errorMessage: string | null;

  dupeSearchItem: DupeSearchItem[];
  detailDupeSearchList: DetailDupeSearchList | null;
  detailDupeSearchItem: DetailDupeSearchItem[];
  stylingItem: StylingItem[];
  likeItem: LikeItem[];

  fetchDupeSaerchHistory: () => Promise<void>;
  fetchDetailDupeSearchList: (searchId: number) => Promise<void>;
  fetchStylingList: () => Promise<void>;
  fetchLikeList: () => Promise<void>;

  reset: () => void;
};

export const useMeStore = create<MeState>((set) => ({
  isLoading: false,
  errorMessage: null,

  dupeSearchItem: [],
  detailDupeSearchList: null,
  detailDupeSearchItem: [],
  stylingItem: [],
  likeItem: [],

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
        errorMessage: '듀프 제품 검색 기록 조회에 실패했습니다.',
      });
    }
  },

  fetchDetailDupeSearchList: async (searchId: number) => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await getDetailDupeSearch(searchId);

      set({
        detailDupeSearchList: res.result,
        detailDupeSearchItem: res.result.results,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: '듀프 제품 검색 기록 상세 조회에 실패했습니다.',
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
        errorMessage: '저장한 스타일링 목록 조회에 실패했습니다.',
      });
    }
  },

  fetchLikeList: async () => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await getLikeList();

      set({
        likeItem: res.result.likeProducts,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: '좋아요한 상품 조회에 실패했습니다.',
      });
    }
  },

  reset: () =>
    set({
      isLoading: false,
      errorMessage: null,
      dupeSearchItem: [],
      stylingItem: [],
      likeItem: [],
    }),
}));
