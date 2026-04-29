import CircleLeftIcon from '../../assets/icons/CircleLeftIcon';
import CircleRightIcon from '../../assets/icons/CircleRightIcon';
import { onboardingData } from '../../constants';
import { useOnboardingStore } from '../../stores/onboardings/onboardingStore';
import StepBar from '../commons/StepBar';

const OnboardingContent = () => {
  const { step, nextStep, prevStep } = useOnboardingStore();

  const current = onboardingData[step - 1];

  return (
    <div className="flex h-full min-h-0 bg-secondary-900">
      <div
        key={step}
        className="w-2/3 h-full min-h-0 p-12.5 flex items-center justify-center animate-[fadeIn_300ms_ease-in-out]"
      >
        <img
          src={current.image}
          className="h-full w-auto object-contain shadow-image-shadow"
        />
      </div>
      <div className="w-1/3 h-full py-12.5 px-12.5 bg-gray-0 flex flex-col gap-10 justify-center">
        {/* 스텝바 */}
        <StepBar />
        {/* 본문 */}
        <div
          key={`text-${step}`}
          className="flex flex-col gap-2.5 animate-[fadeIn_300ms_ease-in-out]"
        >
          <span className="font-bold text-[32px] text-gray-900 whitespace-pre-line">
            {current.title}
          </span>
          <span className="font-normal text-[20px] whitespace-pre-line">
            {current.description}
          </span>
        </div>
        {/* 버튼 */}
        <div className="flex gap-5 items-center justify-start">
          <CircleLeftIcon
            onClick={prevStep}
            className={`size-8 ${
              step === 1
                ? 'text-primary-600'
                : 'text-primary-900 cursor-pointer'
            }`}
          />
          <CircleRightIcon
            onClick={nextStep}
            className={`size-8 ${
              step === 3
                ? 'text-primary-600'
                : 'text-primary-900 cursor-pointer'
            }`}
          />
        </div>
      </div>
    </div>
  );
};

export default OnboardingContent;
