import { useNavigate } from 'react-router-dom';
import useBaseModal from '../../stores/modals/baseModal';
import { Button } from '../commons/Button';
import { useAuthStore } from '../../stores/auth/authStore';

const WithdrawModal = () => {
  const { closeModal } = useBaseModal();
  const { withdraw } = useAuthStore();
  const navigate = useNavigate();

  const handleWithdraw = () => {
    withdraw();
    closeModal();
    navigate('/');
  };

  return (
    <div className="w-112.5 flex flex-col gap-7.5 p-7.5 items-center justify-center bg-screen-default rounded-[14px]">
      {/* 본문 */}
      <div className="flex flex-col gap-2.5 items-center justify-center">
        <span className="typo-body_bold20 text-gray-900">
          회원 정보를 삭제할까요?
        </span>
        <span className="typo-body_thin16 text-gray-900 text-center">
          지금까지 저장된 모든 정보는 삭제되며, <br />
          삭제 후에는 복구가 어렵습니다.
        </span>
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
          onClick={handleWithdraw}
        >
          확인
        </Button>
      </div>
    </div>
  );
};

export default WithdrawModal;
