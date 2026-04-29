import { useNavigate } from 'react-router-dom';
import useBaseModal from '../../stores/modals/baseModal';
import { Button } from '../commons/Button';
import { useStylingStore } from '../../stores/stylings/stylingStore';

const StylingResearchModal = () => {
  const { closeModal } = useBaseModal();
  const navigate = useNavigate();

  const { recommendStyling, detailStyling, stylingLoading } = useStylingStore();

  const productId = detailStyling?.mainProduct.productId;

  return (
    <div className="w-112.5 flex flex-col gap-5 p-7.5 items-center justify-center bg-screen-default rounded-[14px]">
      {/* 본문 */}
      <div className="flex flex-col gap-2.5 items-center justify-center">
        <span className="typo-body_bold16 text-gray-900">
          다른 스타일링 제품을 추천해드릴까요?
        </span>
        <span className="typo-body_thin14 text-gray-900 text-center">
          현재 스타일링 추천을 받고 있는 ‘좋아요한 제품’을 기준으로 다른
          <br />
          스타일링 제품을 추천해드립니다.
        </span>
      </div>
      {/* 버튼 */}
      <div className="w-full flex gap-3">
        <Button
          variant="modal_secondary"
          size="modal"
          fullWidth
          disabled={stylingLoading}
          onClick={closeModal}
        >
          취소
        </Button>
        <Button
          variant="modal_primary"
          size="modal"
          fullWidth
          disabled={stylingLoading}
          onClick={async () => {
            if (!productId) return;

            const result = await recommendStyling(productId);

            if (result) {
              navigate(`/styling/${result.stylingId}`);
            }

            closeModal();
          }}
        >
          확인
        </Button>
      </div>
    </div>
  );
};

export default StylingResearchModal;
