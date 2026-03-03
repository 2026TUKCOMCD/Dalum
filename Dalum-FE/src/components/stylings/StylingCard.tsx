import LikeIcon from '../../assets/icons/LikeIcon';
import LinkIcon from '../../assets/icons/LinkIcon';
import type { StylingItem } from '../../types/stylings/Styling.types';
import { Button } from '../commons/Button';

type Props = {
  item: StylingItem;
};

const StylingCard = ({ item }: Props) => {
  const priceText = new Intl.NumberFormat('ko-KR').format(item.price) + '원';

  return (
    <div className="relative w-fit h-fit flex flex-col gap-2.5 bg-gray-0 rounded-lg p-2.5 shadow-card-shadow group">
      {/* 이미지 영역 */}
      <div className="relative w-50 h-50">
        {item.imageUrl ? (
          <img
            src={item.imageUrl}
            alt={item.name}
            className="max-w-45 max-h-45 rounded-sm object-cover bg-secondary-900"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full rounded-sm bg-secondary-900" />
        )}

        <div className="absolute inset-0 rounded-sm bg-gray-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-between p-1">
          {/* 제품 정보 */}
          <div className="flex flex-col gap-2">
            <span className="typo-body_med12 text-gray-600">{item.brand}</span>
            <div className="flex flex-col gap-1">
              <span className="typo-body_bold14 text-gray-900">
                {item.name}
              </span>

              <div className="flex items-center gap-1">
                {item.discountRate && (
                  <span className="typo-body_bold14 text-button-like">
                    {item.discountRate}%
                  </span>
                )}
                <span className="typo-body_med14">{priceText}</span>
              </div>
            </div>
          </div>

          {/* 버튼 영역 */}
          <div className="flex flex-col gap-2">
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
            >
              좋아요
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StylingCard;
