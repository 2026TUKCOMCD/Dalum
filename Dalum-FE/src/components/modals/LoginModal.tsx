import useBaseModal from "../../stores/modals/baseModal";
import { Button } from "../commons/Button";
import Logo from "../../assets/icons/Logo";
import KakaoIcon from "../../assets/icons/KakaoIcon";
import GoogleIcon from "../../assets/icons/GoogleIcon";
import NaverIcon from "../../assets/icons/NaverIcon";

const LoginModal = () => {
  const { closeModal } = useBaseModal();

  return (
    <div className="w-150 flex flex-col gap-10 p-6 items-center justify-center bg-screen-default rounded-[14px]">
      {/* 닫기 버튼 */}
      <div className="w-full px-1 flex items-center justify-end">
        <div className="w-6 h-6 bg-close cursor-pointer" onClick={closeModal} />
      </div>
      {/* 로고 */}
      <div className="flex flex-col items-center justify-center">
        <Logo className="w-32.5 text-gray-900" />
      </div>
      {/* 버튼 */}
      <div className="w-full flex flex-col gap-3 py-2">
        <Button
          variant="social_kakao"
          size="social"
          fullWidth
          leftIcon={<KakaoIcon className="size-10.5" />}
          onClick={closeModal}
        >
          카카오 회원가입 / 로그인
        </Button>
        <Button
          variant="social_naver"
          size="social"
          fullWidth
          leftIcon={<NaverIcon className="size-10.5" />}
          onClick={closeModal}
        >
          네이버 회원가입 / 로그인
        </Button>
        <Button
          variant="social_google"
          size="social"
          fullWidth
          leftIcon={<GoogleIcon className="size-10.5" />}
          onClick={closeModal}
        >
          구글 회원가입 / 로그인
        </Button>
      </div>
    </div>
  );
};

export default LoginModal;
