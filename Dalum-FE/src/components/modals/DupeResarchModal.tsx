import { useNavigate } from "react-router-dom";
import useBaseModal from "../../stores/modals/baseModal";
import { Button } from "../commons/Button";

const DupeResearchModal = () => {
  const { closeModal } = useBaseModal();
  const navigate = useNavigate();

  return (
    <div className="w-112.5 flex flex-col gap-7.5 p-7.5 items-center justify-center bg-screen-default rounded-[14px]">
      {/* 본문 */}
      <div className="flex flex-col gap-2.5 items-center justify-center">
        <span className="typo-body_bold20 text-gray-900">
          다른 이미지로 듀프 제품을 찾아볼까요?
        </span>
        <span className="typo-body_thin16 text-gray-900 text-center">
          듀프 제품 검색 기록은 마이 페이지에서 <br />
          다시 확인할 수 있습니다.
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
          onClick={() => {
            navigate("/");
            closeModal();
          }}
        >
          확인
        </Button>
      </div>
    </div>
  );
};

export default DupeResearchModal;
