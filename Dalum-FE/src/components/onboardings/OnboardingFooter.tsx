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
      <div className="w-1/2 flex flex-col gap-7.5 justify-center items-center">
        <div className="flex items-center gap-2.5">
          <MiniLogo className="w-auto h-15" />
          <Logo className="w-32.5 h-auto text-primary-900" />
        </div>
        <span className="text-primary-900 font-bold text-[24px]">
          나에게 어울리는 스타일을 더 정확하게!
        </span>
      </div>

      <div className="w-1/2 flex flex-col gap-3">
        <Button
          variant="social_kakao"
          size="social"
          fullWidth
          leftIcon={<KakaoIcon className="size-8" />}
          onClick={() => redirectToSocialLogin('kakao')}
        >
          카카오 회원가입 / 로그인
        </Button>
        <Button
          variant="social_naver"
          size="social"
          fullWidth
          leftIcon={<NaverIcon className="size-8" />}
        >
          네이버 회원가입 / 로그인
        </Button>
        <Button
          variant="social_google"
          size="social"
          fullWidth
          leftIcon={<GoogleIcon className="size-8" />}
        >
          구글 회원가입 / 로그인
        </Button>
      </div>
    </div>
  );
};

export default OnboardingFooter;
