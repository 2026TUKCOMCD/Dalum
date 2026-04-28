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

    const result = await recommendStyling(item.productId);

    if (result) {
      navigate(`/styling/${result.stylingId}`);
    }
  };

  return (
    <div className="w-87.5 h-fit flex items-center justify-start gap-3">
      <div className="h-45 flex justify-center items-center rounded-sm">
        <img
          src={item.imageUrl}
          className="h-full object-contain rounded-sm shadow-image-shadow"
        />
      </div>

      <div className="flex-1 h-45 flex flex-col justify-between py-1.5">
        <div className="flex flex-col gap-2 justify-center items-start">
          {/* 브랜드 */}
          <span className="typo-body_med12 text-gray-600">{item.brand}</span>

          <div className="flex flex-col gap-1 justify-center items-start">
            {/* 제품명 */}
            <span className="typo-body_bold12 text-gray-900 line-clamp-2 break-keep">
              {item.name}
            </span>
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
        <div className="w-full flex gap-2 items-center justify-start">
          <Button
            variant="primary"
            size="card"
            leftIcon={<StyleIcon className="size-3" />}
            onClick={handleClickStyling}
            className="group w-fit px-4 gap-2 rounded-2xl"
          >
            <span className="overflow-hidden whitespace-nowrap">
              스타일링 추천
            </span>
          </Button>
          <Button
            variant="primary"
            size="card"
            leftIcon={<LinkIcon className="size-3" />}
            onClick={handleClickPurchase}
            disabled={!purchaseLink}
          />
          <Button
            variant={isLiked ? 'active_primary' : 'primary'}
            size="card"
            leftIcon={<LikeIcon className="size-3" />}
            onClick={handleClickLike}
            disabled={isLikeLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default LikeProductCard;
