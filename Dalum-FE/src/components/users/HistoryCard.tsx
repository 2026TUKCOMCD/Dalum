import KebabIcon from "../../assets/icons/KebabIcon";

const HistoryCard = () => {
  return (
    <div className="w-fit h-fit flex flex-col gap-2">
      <div className="w-45 h-45 bg-secondary-900 rounded-sm"></div>
      <div className="flex flex-col gap-1 px-1 py-0.5 text-gray-900">
        <div className="w-full h-fit flex items-center justify-between">
          <span className="typo-body_bold12">| 생성일시</span>
          <div>
            <KebabIcon />
          </div>
        </div>
        <span className="typo-body_med12">2026.01.15.(목) 05:28</span>
      </div>
    </div>
  );
};

export default HistoryCard;
