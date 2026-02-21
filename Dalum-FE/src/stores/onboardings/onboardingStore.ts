import { create } from 'zustand';

type OnboardingState = {
  step: number;
  nextStep: () => void;
  prevStep: () => void;
  setStep: (step: number) => void;
};

export const useOnboardingStore = create<OnboardingState>((set) => ({
  step: 1,
  nextStep: () =>
    set((state) => ({
      step: Math.min(state.step + 1, 3),
    })),
  prevStep: () =>
    set((state) => ({
      step: Math.max(state.step - 1, 1),
    })),
  setStep: (step) => set({ step }),
}));
