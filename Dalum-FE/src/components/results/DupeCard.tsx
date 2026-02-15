import ChartIcon from "../../assets/icons/ChartIcon";
import LikeIcon from "../../assets/icons/LikeIcon";
import LinkIcon from "../../assets/icons/LinkIcon";
import { Button } from "../commons/Button";

const DupeCard = () => {
  return (
    <div className="h-fit flex flex-col gap-3 justify-start items-center">
      {/* 제품 사진 */}
      <div className="w-50 h-50 rounded-sm bg-secondary-900" />

      {/* 제품 정보 & 상호작용 버튼 */}
      <div className="w-full h-full flex flex-col justify-between gap-3 px-1">
        {/* 제품 정보 */}
        <div className="flex flex-col gap-2">
          {/* 브랜드명 */}
          <span className="typo-body_med12 text-gray-600">THE OTHER SIDE</span>
          <div className="flex flex-col gap-1">
            {/* 제품명 */}
            <span className="typo-body_bold14 text-gray-900">
              루즈핏 기모 후드티 (5color)
            </span>
            {/* 제품 가격 */}
            <div className="flex items-center justify-start gap-1">
              {/* 할인율 */}
              <span className="typo-body_bold14 text-button-like">38%</span>
              {/* 가격 */}
              <span className="typo-body_med14 text-gray-900">37,000₩</span>
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
