import SearchIcon from "../../assets/icons/SearchIcon";
import type { HistoryItem } from "../../types/me/Me.types";
import { Button } from "../commons/Button";
import HistoryCardList from "./HistoryCardList";

const UserResearchHistory = ({ items }: { items: HistoryItem[] }) => {
  const searchItems = items.filter((i) => i.type === "search");

  return (
    <div className="w-full flex flex-col gap-5">
      <span className="typo-body_bold20">내가 찾은 듀프 제품</span>
      <div className="w-full flex flex-col items-center justify-center rounded-sm border-2 border-gray-500 p-5">
        {searchItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-5">
            <span className="typo-body_bold18 text-gray-700">
              듀프 제품을 검색한 기록이 없어요!
            </span>
            <Button
              variant="primary"
              size="md"
              leftIcon={<SearchIcon className="size-4" />}
            >
              듀프 제품 검색
            </Button>
          </div>
        ) : (
          <HistoryCardList items={searchItems} />
        )}
      </div>
    </div>
  );
};

export default UserResearchHistory;
