import LikeIcon from "../../assets/icons/LikeIcon";
import LinkIcon from "../../assets/icons/LinkIcon";
import StyleIcon from "../../assets/icons/StyleIcon";
import { Button } from "../commons/Button";

const LikeProductCard = () => {
  return (
    <div className="w-100 h-45 flex items-center justify-start gap-3">
      <div className="w-45 h-45 rounded-sm bg-secondary-900"></div>

      <div className="flex-1 h-full flex flex-col justify-between py-1.5">
        <div className="flex flex-col gap-2 justify-center items-start">
          {/* 브랜드 */}
          <span className="typo-body_med12 text-gray-600">THE OTHER SIDE</span>

          <div className="flex flex-col gap-1 justify-center items-start">
            {/* 제품명 */}
            <span className="typo-body_bold14 text-gray-900">
              루즈핏 기모 후드티 (5color)
            </span>
            {/* 가격 */}
            <div className="flex justify-center items-start gap-1">
              <span className="typo-body_bold14 text-button-like">38%</span>
              <span className="typo-body_med14 text-gray-900">37,000₩</span>
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
            스타일링 추천 받기
          </Button>
          <div className="w-full flex items-center justify-center gap-2">
            <Button
              variant="primary"
              size="sm"
              fullWidth
              leftIcon={<LinkIcon className="size-3" />}
              className="flex-1"
            >
              구매처 바로가기
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
