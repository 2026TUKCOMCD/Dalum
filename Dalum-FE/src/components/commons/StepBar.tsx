import { useOnboardingStore } from '../../stores/onboardings/onboardingStore';

const StepBar = () => {
  const { step } = useOnboardingStore();

  return (
    <div className="flex gap-3 items-center justify-start">
      {[1, 2, 3].map((s) => (
        <div
          key={s}
          className={`
            h-2 rounded-full transition-all duration-300
            ${step === s ? 'w-8 bg-primary-900' : 'w-2 bg-primary-600'}
          `}
        />
      ))}
    </div>
  );
};

export default StepBar;
