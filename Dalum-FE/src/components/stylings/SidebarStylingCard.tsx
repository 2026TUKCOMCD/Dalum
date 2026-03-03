import LikeIcon from '../../assets/icons/LikeIcon';
import LinkIcon from '../../assets/icons/LinkIcon';
import type { MainStylingItem } from '../../types/stylings/Styling.types';
import { Button } from '../commons/Button';

type Props = {
  item: MainStylingItem;
};

const SidebarStylingCard = ({ item }: Props) => {
  const priceText = new Intl.NumberFormat('ko-KR').format(item.price) + '원';

  return (
    <div className="w-62.5 h-fit flex flex-col gap-2.5 justify-start items-center bg-gray-0 rounded-lg p-2.5 shadow-card-shadow">
      {/* 제품 사진 */}
      {item.imageUrl ? (
        <img
          src={item.imageUrl}
          alt={item.name}
          className="max-w-57.5 max-h-57.5 rounded-sm object-cover bg-secondary-900"
          loading="lazy"
        />
      ) : (
        <div className="w-57.5 h-57.5 rounded-sm bg-secondary-900" />
      )}
      {/* 제품 정보 */}
      <div className="w-full flex flex-col gap-2">
        {/* 브랜드명 */}
        <span className="typo-body_med12 text-gray-600">{item.brand}</span>
        <div className="flex flex-col gap-1">
          {/* 제품명 */}
          <span className="typo-body_bold14 text-gray-900">{item.name}</span>

          {/* 제품 가격 */}
          <div className="flex items-center justify-start gap-1">
            {/* 할인율 */}
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
            variant="primary"
            size="sm"
            leftIcon={<LinkIcon className="size-3" />}
            fullWidth
            className="flex-1"
          >
            구매 링크
          </Button>
          <Button
            variant="like"
            size="sm"
            leftIcon={<LikeIcon className="size-3" />}
            fullWidth
            className="flex-1"
          >
            좋아요
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SidebarStylingCard;
