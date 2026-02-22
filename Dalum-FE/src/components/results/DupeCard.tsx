import ChartIcon from '../../assets/icons/ChartIcon';
import LikeIcon from '../../assets/icons/LikeIcon';
import LinkIcon from '../../assets/icons/LinkIcon';
import useBaseModal from '../../stores/modals/baseModal';
import { useProductStore } from '../../stores/products/productStore';
import type { DetailDupeSearchItem } from '../../types/me/Me.types';
import { Button } from '../commons/Button';

type DupeCardProps = {
  item: DetailDupeSearchItem;
};

const DupeCard = ({ item }: DupeCardProps) => {
  const { openModal } = useBaseModal();

  const isLiked = useProductStore(
    (s) => s.likeStatusById[item.productId] ?? false
  );
  const isLikeLoading = useProductStore(
    (s) => s.isLoadingById[item.productId] ?? false
  );
  const toggleLikeStatus = useProductStore((s) => s.toggleLikeStatus);

  const priceText = new Intl.NumberFormat('ko-KR').format(item.price) + '원';

  const handleClickPurchase = () => {
    if (!item.purchaseUrl) return;
    window.open(item.purchaseUrl, '_blank', 'noopener,noreferrer');
  };

  const handleClickLike = () => {
    if (isLikeLoading) return;
    toggleLikeStatus(item.productId);
  };

  return (
    <div className="max-w-50 h-fit flex flex-col gap-3 justify-start items-center">
      <div className="w-50 h-50 rounded-sm flex items-center justify-center">
        {/* 제품 사진 */}
        {item.imageUrl ? (
          <img
            src={item.imageUrl}
            alt={item.name}
            className="w-full h-auto rounded-sm object-cover bg-secondary-900"
            loading="lazy"
          />
        ) : (
          <div className="w-50 h-50 rounded-sm bg-secondary-900" />
        )}
      </div>
      {/* 제품 정보 & 상호작용 버튼 */}
      <div className="w-full h-full flex flex-col justify-between gap-3 px-1">
        {/* 제품 정보 */}
        <div className="flex flex-col gap-2">
          {/* 브랜드명 */}
          <span className="typo-body_med12 text-gray-600">{item.brand}</span>
          <div className="flex flex-col gap-1">
            {/* 제품명 */}
            <span className="typo-body_bold14 text-gray-900">{item.name}</span>

            {/* 제품 가격 */}
            <div className="flex items-center justify-start gap-1">
              {/* 할인율 */}
              {/* 임시처리 API 수정 후 주석 해제 */}
              {/* {typeof item.discountRate === 'number' && (
                <span className="typo-body_bold14 text-button-like">
                  {item.discountRate}%
                </span>
              )} */}
              {/* 가격 */}
              <span className="typo-body_med14 text-gray-900">{priceText}</span>
            </div>
          </div>
        </div>

        {/* 상호 작용 버튼 */}
        <div className="w-full flex flex-col gap-2">
          <div className="w-full flex items-center justify-start gap-2">
            <Button
              variant="gray"
              size="sm"
              leftIcon={<ChartIcon className="size-3" />}
              fullWidth
              className="flex-1"
              onClick={() => openModal('similarityCheckModal')}
            >
              유사도 확인
            </Button>
            <Button
              variant={isLiked ? 'active_like' : 'like'}
              size="sm"
              leftIcon={<LikeIcon className="size-3" />}
              onClick={handleClickLike}
              disabled={isLikeLoading}
            >
              좋아요
            </Button>
          </div>
          <Button
            variant="primary"
            size="sm"
            fullWidth
            leftIcon={<LinkIcon className="size-3" />}
            onClick={handleClickPurchase}
            disabled={!item.purchaseUrl}
          >
            구매 링크
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DupeCard;
