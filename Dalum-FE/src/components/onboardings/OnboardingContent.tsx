import CircleLeftIcon from '../../assets/icons/CircleLeftIcon';
import CircleRightIcon from '../../assets/icons/CircleRightIcon';
import StepBar from '../commons/StepBar';

const OnboardingContent = () => {
  return (
    <div className="flex h-full min-h-0 bg-secondary-900">
      <div className="w-2/3 h-full min-h-0 p-12.5 flex items-center justify-center">
        <img
          src="/image/onboarding_1.png"
          className="h-full w-auto object-contain shadow-image-shadow"
        />
      </div>
      <div className="w-1/3 h-full py-12.5 px-12.5 bg-gray-0 flex flex-col gap-10 justify-center">
        {/* 스텝바 */}
        <StepBar />
        {/* 본문 */}
        <div className="flex flex-col gap-2.5">
          <span className="font-bold text-[32px] gray-900">
            좋아하는 제품에 어울리는
            <br />
            스타일링 추천받기
          </span>
          <span className="font-normal text-[20px]">
            마음에 드는 듀프 제품에 어울리는 제품을
            <br />
            종류 별로 추천 받을 수 있습니다.
          </span>
        </div>
        {/* 버튼 */}
        <div className="flex gap-5 items-center justify-start">
          <CircleLeftIcon className="size-8 text-primary-900" />
          <CircleRightIcon className="size-8 text-primary-600" />
        </div>
      </div>
    </div>
  );
};

export default OnboardingContent;
