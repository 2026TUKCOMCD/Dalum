import KebabIcon from "../../assets/icons/KebabIcon";
import type { DupeSearchItem, StylingItem } from "../../types/me/Me.types";
import { formatDate, isDupeSearchItem } from "../../utils";

type Props = {
  item: DupeSearchItem | StylingItem;
  onMenuClick?: (item: DupeSearchItem | StylingItem) => void;
};

const HistoryCard = ({ item, onMenuClick }: Props) => {
  const imageUrl = isDupeSearchItem(item)
    ? `${item.inputImageUrl}`
    : `${item.mainProductImageUrl}`;

  const time = isDupeSearchItem(item)
    ? `${item.searchTime}`
    : `${item.createdAt}`;

  return (
    <div className="w-45 h-fit flex flex-col gap-2 cursor-pointer">
      <img src={imageUrl} className="w-45 h-45 bg-none rounded-sm" />
      <div className="flex flex-col gap-1 px-1 py-0.5 text-gray-900">
        <div className="w-full h-fit flex items-center justify-between">
          <span className="typo-body_bold12">| 검색일시</span>
          <button type="button" onClick={() => onMenuClick?.(item)}>
            <KebabIcon />
          </button>
        </div>
        <span className="typo-body_med12">{formatDate(new Date(time))}</span>
      </div>
    </div>
  );
};

export default HistoryCard;
