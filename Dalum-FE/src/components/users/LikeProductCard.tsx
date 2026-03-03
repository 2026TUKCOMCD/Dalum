import LikeIcon from '../../assets/icons/LikeIcon';
import LinkIcon from '../../assets/icons/LinkIcon';
import StyleIcon from '../../assets/icons/StyleIcon';
import type { LikeItem } from '../../types/me/Me.types';
import { Button } from '../commons/Button';
import { useProductStore } from '../../stores/products/productStore';
import { useStylingStore } from '../../stores/stylings/stylingStore';
import { useNavigate } from 'react-router-dom';

type Props = {
  item: LikeItem;
};

const LikeProductCard = ({ item }: Props) => {
  const navigate = useNavigate();

  const isLiked = useProductStore(
    (s) => s.likeStatusById[item.productId] ?? false
  );
  const isLikeLoading = useProductStore(
    (s) => s.isLoadingById[item.productId] ?? false
  );
  const toggleLikeStatus = useProductStore((s) => s.toggleLikeStatus);

  const { recommendStyling, isLoading } = useStylingStore();

  const priceText =
    new Intl.NumberFormat('ko-KR').format(item.discount_price) + '원';

  const purchaseLink = item.purchase_link;

  // 구매 링크 버튼 클릭 핸들러
  const handleClickPurchase = () => {
    if (!purchaseLink) return;
    window.open(purchaseLink, '_blank', 'noopener,noreferrer');
  };

  const handleClickLike = () => {
    if (isLikeLoading) return;
    toggleLikeStatus(item.productId);
  };

  const handleClickStyling = async () => {
    if (isLoading) return;
    await recommendStyling(item.productId);
    navigate('/styling');
  };

  return (
    <div className="w-100 h-45 flex items-center justify-start gap-3">
      <div className="w-45 h-45 flex justify-center items-center">
        <img
          src={item.imageUrl}
          className="max-w-45 max-h-45 rounded-sm bg-none"
        />
      </div>

      <div className="flex-1 h-full flex flex-col justify-between py-1.5">
        <div className="flex flex-col gap-2 justify-center items-start">
          {/* 브랜드 */}
          <span className="typo-body_med12 text-gray-600">{item.brand}</span>

          <div className="flex flex-col gap-1 justify-center items-start">
            {/* 제품명 */}
            <span className="typo-body_bold14 text-gray-900">{item.name}</span>
            {/* 가격 */}
            <div className="flex justify-center items-start gap-1">
              <span className="typo-body_bold14 text-button-like">
                {item.discount_rate}%
              </span>
              <span className="typo-body_med14 text-gray-900">{priceText}</span>
            </div>
          </div>
        </div>

        {/* 버튼 */}
        <div className="w-full flex flex-col gap-2 items-center justify-center">
          <Button
            variant="gray"
            size="sm"
            fullWidth
            leftIcon={<StyleIcon className="size-3" />}
            onClick={handleClickStyling}
          >
            스타일링 추천
          </Button>
          <div className="w-full flex items-center justify-center gap-2">
            <Button
              variant="primary"
              size="sm"
              fullWidth
              leftIcon={<LinkIcon className="size-3" />}
              className="flex-1"
              onClick={handleClickPurchase}
              disabled={!purchaseLink}
            >
              구매 링크
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
        </div>
      </div>
    </div>
  );
};

export default LikeProductCard;
