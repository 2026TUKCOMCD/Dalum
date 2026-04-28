import useBaseModal from '../../stores/modals/baseModal';
import { Button } from '../commons/Button';
import { useStylingStore } from '../../stores/stylings/stylingStore';

const SaveStylingModal = () => {
  const { closeModal } = useBaseModal();

  const { saveStyling, stylingResult } = useStylingStore();

  return (
    <div className="w-112.5 flex flex-col gap-5 p-7.5 items-center justify-center bg-screen-default rounded-[14px]">
      {/* 본문 */}
      <div className="flex flex-col gap-2.5 items-center justify-center">
        <span className="typo-body_bold16 text-gray-900">
          해당 페이지의 스타일링을 저장할까요?
        </span>
        <span className="typo-body_thin14 text-gray-900 text-center">
          저장된 스타일링은 마이 페이지에서 확인할 수 있습니다.
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
            if (stylingResult?.stylingId !== undefined) {
              saveStyling(stylingResult.stylingId);
              closeModal();
            }
          }}
        >
          확인
        </Button>
      </div>
    </div>
  );
};

export default SaveStylingModal;
