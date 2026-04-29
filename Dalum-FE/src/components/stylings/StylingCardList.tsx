import { CATEGORY_MAP } from '../../constants';
import type {
  MainStylingItem,
  ResultStylingItem,
} from '../../types/stylings/Styling.types';
import { groupByCategory } from '../../utils';
import CategoryCard from './CategoryCard';
import ServiceCard from './ServiceCard';

type Props = {
  items: ResultStylingItem[];
  mainItem: MainStylingItem;
  index: number;
};

// const StylingCardList = ({ items }: Props) => {
//   const cards = items.slice(0, 5);

//   return (
//     <div className="w-full h-full grid grid-cols-3 grid-rows-2 gap-15 justify-center justify-items-center items-center">
//       <ServiceCard />

//       {cards.map((item) => (
//         <StylingCard key={item.productId} item={item} />
//       ))}

//       {Array.from({ length: Math.max(0, 5 - cards.length) }).map((_, idx) => (
//         <div
//           key={`empty-${idx}`}
//           className="w-fit h-fit flex flex-col gap-2.5 bg-gray-0 rounded-lg p-2.5 shadow-card-shadow opacity-40"
//         >
//           <div className="w-50 h-50 rounded-sm bg-secondary-900" />
//         </div>
//       ))}
//     </div>
//   );
// };

const StylingCardList = ({ items, mainItem, index }: Props) => {
  const categories = CATEGORY_MAP[mainItem.category];

  const grouped = groupByCategory(items);

  return (
    <div className="grid grid-cols-3 grid-rows-2 gap-15">
      <ServiceCard />

      {categories.map((category) => (
        <CategoryCard
          key={category}
          category={category}
          item={grouped[category]?.[index]}
        />
      ))}
    </div>
  );
};

export default StylingCardList;
