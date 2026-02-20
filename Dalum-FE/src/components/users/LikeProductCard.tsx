import { useNavigate } from "react-router-dom";
import LikeIcon from "../../assets/icons/LikeIcon";
import LinkIcon from "../../assets/icons/LinkIcon";
import StyleIcon from "../../assets/icons/StyleIcon";
import type { LikeItem } from "../../types/me/Me.types";
import { Button } from "../commons/Button";

type Props = {
  item: LikeItem;
};

const LikeProductCard = ({ item }: Props) => {
  const navigate = useNavigate();

  const priceText =
    new Intl.NumberFormat("ko-KR").format(item.discount_price) + "원";

  const purchaseLink = item.purchase_link;

  // 구매 링크 버튼 클릭 핸들러
  const handlePurchase = () => {
    navigate(`${purchaseLink}`);
  };

  return (
    <div className="w-100 h-45 flex items-center justify-start gap-3">
      <img src={item.imageUrl} className="w-45 h-45 rounded-sm bg-none" />

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
              onClick={handlePurchase}
            >
              구매 링크
            </Button>
            <Button
              variant="like"
              size="sm"
              leftIcon={<LikeIcon className="size-3" />}
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
