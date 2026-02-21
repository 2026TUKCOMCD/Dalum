import { useEffect } from "react";
import { useMeStore } from "../../stores/me/meStore";
import HistoryCardList from "./HistoryCardList";

const UserSavedStyling = () => {
  const { stylingItem, fetchStylingList } = useMeStore();

  useEffect(() => {
    fetchStylingList();
  }, [fetchStylingList]);

  return (
    <div className="w-full flex flex-col gap-5">
      <span className="typo-body_bold20">저장한 스타일링</span>
      <div className="w-full flex flex-col items-center justify-center gap-5 rounded-sm border-2 border-gray-500">
        {stylingItem.length === 0 ? (
          <div className="flex flex-col justify-center items-center gap-2.5 p-5">
            <span className="typo-body_bold18 text-gray-700">
              저장한 스타일링이 없어요!
            </span>
            <span className="typo-body_med16 text-gray-600 text-center">
              마음에 드는 제품을 기반으로 스타일링을 추천 받을 수 있어요! <br />
              좋아요한 제품으로 스타일링을 추천 받아 보세요!
            </span>
          </div>
        ) : (
          <HistoryCardList items={stylingItem} />
        )}
      </div>
    </div>
  );
};

export default UserSavedStyling;
