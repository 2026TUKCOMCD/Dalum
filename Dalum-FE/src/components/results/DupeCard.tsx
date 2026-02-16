import ChartIcon from "../../assets/icons/ChartIcon";
import LikeIcon from "../../assets/icons/LikeIcon";
import LinkIcon from "../../assets/icons/LinkIcon";
import type { DupeItem } from "../../mocks/dupeMockData";
import { Button } from "../commons/Button";

type DupeCardProps = {
  item: DupeItem;
};

const DupeCard = ({ item }: DupeCardProps) => {
  const priceText = new Intl.NumberFormat("ko-KR").format(item.price) + "원";

  return (
    <div className="max-w-50 h-fit flex flex-col gap-3 justify-start items-center">
      {/* 제품 사진 */}
      {item.imageUrl ? (
        <img
          src={item.imageUrl}
          alt={item.name}
          className="w-50 h-50 rounded-sm object-cover bg-secondary-900"
          loading="lazy"
        />
      ) : (
        <div className="w-50 h-50 rounded-sm bg-secondary-900" />
      )}
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
              {typeof item.discountRate === "number" && (
                <span className="typo-body_bold14 text-button-like">
                  {item.discountRate}%
                </span>
              )}
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
            >
              유사도 확인하기
            </Button>
            <Button
              variant="like"
              size="sm"
              leftIcon={<LikeIcon className="size-3" />}
            >
              좋아요
            </Button>
          </div>
          <Button
            variant="primary"
            size="sm"
            fullWidth
            leftIcon={<LinkIcon className="size-3" />}
          >
            구매처 바로가기
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DupeCard;
