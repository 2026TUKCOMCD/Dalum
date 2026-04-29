import useBaseModal from '../../stores/modals/baseModal';
import { Button } from '../commons/Button';
import { useMeStore } from '../../stores/me/meStore';

const HistoryDeleteModal = () => {
  const { closeModal } = useBaseModal();
  const {
    deleteTarget,
    deleteDupeHistory,
    deleteStylingHistory,
    setDeleteTarget,
  } = useMeStore();

  const handleDelete = async () => {
    if (!deleteTarget) return;

    if ('searchLogId' in deleteTarget) {
      await deleteDupeHistory(deleteTarget.searchLogId);
    } else {
      await deleteStylingHistory(deleteTarget.stylingId);
    }

    setDeleteTarget(null);
    closeModal();
  };

  return (
    <div className="w-112.5 flex flex-col gap-5 p-7.5 items-center justify-center bg-screen-default rounded-[14px]">
      {/* 본문 */}
      <div className="flex flex-col gap-2.5 items-center justify-center">
        <span className="typo-body_bold16 text-gray-900">
          기록을 삭제할까요?
        </span>
        <span className="typo-body_thin14 text-gray-900 text-center">
          삭제된 기록은 복구할 수 없습니다.
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
          onClick={handleDelete}
        >
          확인
        </Button>
      </div>
    </div>
  );
};

export default HistoryDeleteModal;
