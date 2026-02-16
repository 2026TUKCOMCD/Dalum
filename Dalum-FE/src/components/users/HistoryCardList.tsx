import type { HistoryItem } from "../../types/me/Me.types";
import HistoryCard from "./HistoryCard";

type Props = {
  items: HistoryItem[];
  onMenuClick?: (item: HistoryItem) => void;
};

const HistoryCardList = ({ items, onMenuClick }: Props) => {
  return (
    <div className="w-full flex overflow-x-auto scrollbar-hide">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <div key={item.id} className="flex items-center">
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
