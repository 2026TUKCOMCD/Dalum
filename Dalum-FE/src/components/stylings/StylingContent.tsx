import { useState } from 'react';
import type {
  MainStylingItem,
  ResultStylingItem,
} from '../../types/stylings/Styling.types';
import Pagination from '../commons/Pagination';
import StylingCardList from './StylingCardList';
import { CATEGORY_MAP } from '../../constants';
import { groupByCategory } from '../../utils';

type Props = {
  items: ResultStylingItem[];
  mainItem: MainStylingItem;
};

const StylingContent = ({ items, mainItem }: Props) => {
  const [index, setIndex] = useState(0);

  const categories = CATEGORY_MAP[mainItem.category];

  const grouped = groupByCategory(items);

  const total = Math.max(
    ...categories.map((category) => grouped[category]?.length ?? 0)
  );

  return (
    <div className="w-full h-full py-12.5 px-12.5 flex flex-col items-center justify-between gap-12.5">
      <div className="flex flex-col w-full h-full items-center justify-between">
        <StylingCardList items={items} mainItem={mainItem} index={index} />

        <Pagination total={total} current={index} onChange={setIndex} />
      </div>
    </div>
  );
};

export default StylingContent;
