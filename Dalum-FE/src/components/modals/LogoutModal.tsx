import { useNavigate } from 'react-router-dom';
import useBaseModal from '../../stores/modals/baseModal';
import { Button } from '../commons/Button';
import { useAuthStore } from '../../stores/auth/authStore';

const LogoutModal = () => {
  const { closeModal } = useBaseModal();
  const { logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    try {
      logout();
      navigate('/');
      closeModal();
    } catch {
      alert('로그아웃에 실패했습니다. 다시 시도해주세요.');
    }
  };

  return (
    <div className="w-112.5 flex flex-col gap-5 p-7.5 items-center justify-center bg-screen-default rounded-[14px]">
      {/* 본문 */}
      <div className="flex flex-col gap-2.5 items-center justify-center">
        <span className="typo-body_bold16 text-gray-900">로그아웃할까요?</span>
      </div>
      {/* 버튼 */}
      <div className="w-full flex gap-3">
        <Button
          variant="modal_secondary"
          size="modal"
          fullWidth
          onClick={closeModal}
        >
          취소
        </Button>
        <Button
          variant="modal_primary"
          size="modal"
          fullWidth
          onClick={() => {
            handleLogout();
          }}
        >
          확인
        </Button>
      </div>
    </div>
  );
};

export default LogoutModal;
