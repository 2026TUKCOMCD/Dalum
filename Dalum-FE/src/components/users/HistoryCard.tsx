import KebabIcon from "../../assets/icons/KebabIcon";
import type { DupeSearchItem } from "../../types/me/Me.types";
import { formatDate } from "../../utils";

type Props = {
  item: DupeSearchItem;
  onMenuClick?: (item: DupeSearchItem) => void;
};

const HistoryCard = ({ item, onMenuClick }: Props) => {
  return (
    <div className="w-45 h-fit flex flex-col gap-2">
      <img src={item.inputImageUrl} className="w-45 h-45 bg-none rounded-sm" />
      <div className="flex flex-col gap-1 px-1 py-0.5 text-gray-900">
        <div className="w-full h-fit flex items-center justify-between">
          <span className="typo-body_bold12">| 검색일시</span>
          <button type="button" onClick={() => onMenuClick?.(item)}>
            <KebabIcon />
          </button>
        </div>
        <span className="typo-body_med12">
          {formatDate(new Date(item.searchTime))}
        </span>
      </div>
    </div>
  );
};

export default HistoryCard;
