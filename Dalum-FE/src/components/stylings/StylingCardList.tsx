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
