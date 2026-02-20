import { create } from "zustand";
import type { MasterTokenItem } from "../../types/auth/Auth.types";
import createMasterToken from "../../services/auth/getMasterToken";
import logoutAccount from "../../services/auth/logoutAccount";

type AuthState = {
  isLoading: boolean;
  errorMessage: string | null;

  masterToken: MasterTokenItem | null;
  accessToken: string | null;
  refreshToken: string | null;

  createToken: () => Promise<void>;

  logout: () => Promise<void>;
  reset: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  isLoading: false,
  errorMessage: null,

  masterToken: null,
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
        errorMessage: "마스터 토큰 생성에 실패했습니다.",
      });
    }
  },

  logout: async () => {
    try {
      await logoutAccount();

      set({
        isLoading: false,
      });

      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
    } catch {
      set({
        isLoading: false,
        errorMessage: "로그아웃에 실패했습니다.",
      });
    }
  },

  reset: () =>
    set({
      isLoading: false,
      errorMessage: null,
      masterToken: null,
    }),
}));
