import GoogleIcon from '../../assets/icons/GoogleIcon';
import KakaoIcon from '../../assets/icons/KakaoIcon';
import Logo from '../../assets/icons/Logo';
import MiniLogo from '../../assets/icons/MiniLogo';
import NaverIcon from '../../assets/icons/NaverIcon';
import { redirectToSocialLogin } from '../../services/auth/socialLogin';
import { Button } from '../commons/Button';

const OnboardingFooter = () => {
  return (
    <div className="flex justify-between items-center w-full px-10 py-10 bg-gray-0 shadow-footer-shadow">
      <div className="w-1/2 flex flex-col gap-2.5 justify-center items-center">
        <div className="flex items-center gap-1.5">
          <MiniLogo className="w-auto h-12" />
          <Logo className="w-25 h-auto text-primary-900" />
        </div>
        <span className="text-primary-900 font-bold text-[24px]">
          나에게 어울리는 스타일을 더 정확하게!
        </span>
      </div>

      <div className="w-1/2 flex flex-col gap-5 justify-center items-center">
        <span className="text-primary-900 font-bold text-[20px]">
          SNS 계정을 이용해 시작해 보세요!
        </span>
        <div className="w-full flex justify-center items-center gap-3">
          <Button
            variant="onboarding_kakao"
            size="onboarding"
            fullWidth
            leftIcon={<KakaoIcon className="size-8" />}
            onClick={() => redirectToSocialLogin('kakao')}
          >
            카카오로 시작하기
          </Button>
          <Button
            variant="onboarding_naver"
            size="onboarding"
            fullWidth
            leftIcon={<NaverIcon className="size-8" />}
          >
            네이버로 시작하기
          </Button>
          <Button
            variant="onboarding_google"
            size="onboarding"
            fullWidth
            leftIcon={<GoogleIcon className="size-8" />}
          >
            구글로 시작하기
          </Button>
        </div>
      </div>
    </div>
  );
};

export default OnboardingFooter;
