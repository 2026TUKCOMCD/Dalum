import { create } from "zustand";
import type { MasterTokenItem } from "../../types/auth/Auth.types";
import createMasterToken from "../../services/auth/getMasterToken";

type AuthState = {
  isLoading: boolean;
  errorMessage: string | null;

  masterToken: MasterTokenItem | null;

  createToken: () => Promise<void>;
  reset: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  isLoading: false,
  errorMessage: null,

  masterToken: null,

  createToken: async () => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await createMasterToken();

      set({
        masterToken: res.result,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: "마스터 토큰 생성에 실패했습니다.",
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
