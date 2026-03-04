import { create } from 'zustand';
import type {
  MasterTokenItem,
  ReissueTokenItem,
} from '../../types/auth/Auth.types';
import createMasterToken from '../../services/auth/getMasterToken';
import logoutAccount from '../../services/auth/logoutAccount';
import withdrawAccount from '../../services/auth/withdrawAccount';
import reissueToken from '../../services/auth/reissueToken';

type AuthState = {
  isLoading: boolean;
  errorMessage: string | null;

  masterToken: MasterTokenItem | null;
  userToken: ReissueTokenItem | null;
  accessToken: string | null;
  refreshToken: string | null;

  createToken: () => Promise<void>;
  reissueToken: () => Promise<void>;

  logout: () => Promise<void>;
  withdraw: () => Promise<void>;
  reset: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  isLoading: false,
  errorMessage: null,

  masterToken: null,
  userToken: null,
  accessToken: null,
  refreshToken: null,

  createToken: async () => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await createMasterToken();

      set({
        masterToken: res.result,
        accessToken: res.result.accessToken,
        refreshToken: res.result.refreshToken,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: '마스터 토큰 생성에 실패했습니다.',
      });
    }
  },

  reissueToken: async () => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await reissueToken();

      set({
        userToken: res.result,
        accessToken: res.result.accessToken,
        refreshToken: res.result.refreshToken,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: '엑세스 토큰 재발급에 실패했습니다.',
      });
    }
  },

  logout: async () => {
    try {
      await logoutAccount();

      set({
        isLoading: false,
      });

      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    } catch {
      set({
        isLoading: false,
        errorMessage: '로그아웃에 실패했습니다.',
      });
    }
  },

  withdraw: async () => {
    try {
      await withdrawAccount();

      set({
        isLoading: false,
      });

      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    } catch {
      set({
        isLoading: false,
        errorMessage: '회원탈퇴에 실패했습니다.',
      });
    }
  },

  reset: () =>
    set({
      isLoading: false,
      errorMessage: null,
      // masterToken: null,
      userToken: null,
    }),
}));
