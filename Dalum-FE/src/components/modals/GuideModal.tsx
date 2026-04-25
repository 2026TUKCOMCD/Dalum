import useBaseModal from '../../stores/modals/baseModal';
import CloseIcon from '../../assets/icons/CloseIcon';
import StepBar from '../commons/StepBar';
import { useOnboardingStore } from '../../stores/onboardings/onboardingStore';
import { guideData } from '../../constants';
import CircleLeftIcon from '../../assets/icons/CircleLeftIcon';
import CircleRightIcon from '../../assets/icons/CircleRightIcon';

const GuideModal = () => {
  const { closeModal } = useBaseModal();
  const { step, nextStep, prevStep, reset } = useOnboardingStore();

  const current = guideData[step - 1];

  return (
    <div className="w-150 flex flex-col gap-7.5 p-7.5 items-center justify-center bg-screen-default rounded-[14px]">
      {/* 닫기 버튼 */}
      <div className="w-full px-1 flex items-center justify-end">
        <CloseIcon
          className="size-6 cursor-pointer text-gray-900"
          onClick={() => {
            closeModal();
            reset();
          }}
        />
      </div>
      <img key={step} src={current.image} />
      <StepBar />
      <div className="w-full flex items-center gap-7.5">
        <div className="w-7 h-7">
          <CircleLeftIcon
            onClick={prevStep}
            className={`size-7 ${
              step === 1
                ? 'text-primary-600'
                : 'text-primary-900 cursor-pointer'
            }`}
          />
        </div>
        <span
          key={step}
          className="w-full typo-body_thin14 text-gray-900 whitespace-pre-line animate-[fadeIn_300ms_ease-in-out]"
        >
          {current.description}
        </span>
        <div className="w-7 h-7">
          <CircleRightIcon
            onClick={nextStep}
            className={`size-7 ${
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

export default GuideModal;
