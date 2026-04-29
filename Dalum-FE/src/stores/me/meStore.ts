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
import deleteDupeHistory from '../../services/me/deleteDupeHistory';
import deleteStylingHistory from '../../services/me/deleteStylingHistory';

type DeleteTarget = DupeSearchItem | StylingItem | null;

type MeState = {
  isLoading: boolean;
  errorMessage: string | null;

  dupeSearchItem: DupeSearchItem[];
  detailDupeSearchList: DetailDupeSearchList | null;
  detailDupeSearchItem: DetailDupeSearchItem[];
  stylingItem: StylingItem[];
  likeItem: LikeItem[];
  deleteTarget: DeleteTarget;

  fetchDupeSaerchHistory: () => Promise<void>;
  fetchDetailDupeSearchList: (searchId: number) => Promise<void>;
  fetchStylingList: () => Promise<void>;
  fetchLikeList: () => Promise<void>;
  deleteDupeHistory: (searchId: number) => Promise<void>;
  deleteStylingHistory: (stylingId: number) => Promise<void>;
  setDeleteTarget: (item: DeleteTarget) => void;

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
  deleteTarget: null,

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

  deleteDupeHistory: async (searchId: number) => {
    set({ isLoading: true, errorMessage: null });

    try {
      await deleteDupeHistory(searchId);

      set((state) => ({
        dupeSearchItem: state.dupeSearchItem.filter(
          (item) => item.searchLogId !== searchId
        ),
        isLoading: false,
      }));
    } catch {
      set({
        isLoading: false,
        errorMessage: '듀프 제품 검색 기록 삭제에 실패했습니다.',
      });
    }
  },

  deleteStylingHistory: async (stylingId: number) => {
    set({ isLoading: true, errorMessage: null });

    try {
      await deleteStylingHistory(stylingId);

      set((state) => ({
        stylingItem: state.stylingItem.filter(
          (item) => item.stylingId !== stylingId
        ),
        isLoading: false,
      }));
    } catch {
      set({
        isLoading: false,
        errorMessage: '저장한 스타일링 삭제에 실패했습니다.',
      });
    }
  },

  setDeleteTarget: (item) => set({ deleteTarget: item }),

  reset: () =>
    set({
      isLoading: false,
      errorMessage: null,
      dupeSearchItem: [],
      stylingItem: [],
      likeItem: [],
    }),
}));
