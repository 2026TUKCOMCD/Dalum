import type { LikeItem } from "../../types/me/Me.types";
import LikeProductCard from "./LikeProductCard";

type Props = {
  items: LikeItem[];
};

const LikeProductCardList = ({ items }: Props) => {
  return (
    <div className="w-full flex overflow-x-auto scrollbar-hide">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <div key={item.productId} className="flex items-center">
            <LikeProductCard item={item} />

            {!isLast && (
              <div className="w-[0.5px] h-full mx-6.25 bg-gray-500" />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default LikeProductCardList;
