import { stylingMockData } from "../../mocks/stylingMockData";
import ServiceCard from "./ServiceCard";
import StylingCard from "./StylingCard";

const StylingCardList = () => {
  const cards = stylingMockData.slice(0, 5);

  return (
    <div className="w-full h-full grid grid-cols-3 grid-rows-2 gap-15 justify-center justify-items-center items-center">
      <ServiceCard />

      {cards.map((item) => (
        <StylingCard key={item.id} item={item} />
      ))}

      {Array.from({ length: Math.max(0, 5 - cards.length) }).map((_, idx) => (
        <div
          key={`empty-${idx}`}
          className="w-fit h-fit flex flex-col gap-2.5 bg-gray-0 rounded-lg p-2.5 shadow-card-shadow opacity-40"
        >
          <div className="w-50 h-50 rounded-sm bg-secondary-900" />
        </div>
      ))}
    </div>
  );
};

export default StylingCardList;
