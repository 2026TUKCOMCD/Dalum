import type { DupeSearchItem, StylingItem } from "../../types/me/Me.types";
import { isDupeSearchItem } from "../../utils";
import HistoryCard from "./HistoryCard";

type Props = {
  items: DupeSearchItem[] | StylingItem[];
  onMenuClick?: (item: DupeSearchItem | StylingItem) => void;
};

const HistoryCardList = ({ items, onMenuClick }: Props) => {
  return (
    <div className="w-full flex overflow-x-auto scrollbar-hide p-5">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        const key = isDupeSearchItem(item)
          ? `search-${item.searchLogId}`
          : `styling-${item.stylingId}`;

        return (
          <div key={key} className="flex items-center">
            <HistoryCard item={item} onMenuClick={onMenuClick} />

            {!isLast && (
              <div className="w-[0.5px] h-full mx-6.25 bg-gray-500" />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default HistoryCardList;
