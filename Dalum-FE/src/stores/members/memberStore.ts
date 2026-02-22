import { create } from "zustand";
import type { UserItem } from "../../types/members/Member.types";
import getUserInfo from "../../services/members/getUserInfo";

type MemberState = {
  isLoading: boolean;
  errorMessage: string | null;

  userData: UserItem | null;

  fetchUser: () => Promise<void>;
  reset: () => void;
};

export const useMemberStore = create<MemberState>((set) => ({
  isLoading: false,
  errorMessage: null,

  userData: null,

  fetchUser: async () => {
    set({ isLoading: true, errorMessage: null });

    try {
      const res = await getUserInfo();
      console.log(res);

      set({
        userData: res.result,
        isLoading: false,
      });
    } catch {
      set({
        isLoading: false,
        errorMessage: "사용자 정보 조회에 실패했습니다.",
      });
    }
  },

  reset: () =>
    set({
      isLoading: false,
      errorMessage: null,
      userData: null,
    }),
}));
