import StylingCard from './StylingCard';
import type { ResultStylingItem } from '../../types/stylings/Styling.types';
import { CATEGORY_LABEL_MAP } from '../../constants';

type CategoryCardProps = {
  category: string;
  item?: ResultStylingItem;
};

const CategoryCard = ({ item, category }: CategoryCardProps) => {
  const label = CATEGORY_LABEL_MAP[category] ?? category;

  if (!item) {
    return (
      <div className="w-55 h-55 flex items-center justify-center bg-gray-0 rounded-lg border border-primary-600 text-primary-900 typo-body_med16 text-center">
        어울리는 '{label}' 상품을
        <br />
        찾지 못했어요...
      </div>
    );
  }

  return (
    <>
      <StylingCard item={item} />
    </>
  );
};

export default CategoryCard;
