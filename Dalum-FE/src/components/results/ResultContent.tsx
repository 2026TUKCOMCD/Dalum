import { useEffect, useMemo, useRef, useState } from 'react';
import InfoIcon from '../../assets/icons/InfoIcon';
import useBaseModal from '../../stores/modals/baseModal';
import type { DetailDupeSearchItem } from '../../types/me/Me.types';
import { CATEGORY_LABEL_MAP, SCORE_THRESHOLD_MAP } from '../../constants';
import DupeCard from './DupeCard';
import ResultFilter from './ResultFilter';

type Props = {
  items: DetailDupeSearchItem[];
  priceRange?: { minPrice: number | null; maxPrice: number | null };
};

const ResultContent = ({ items, priceRange }: Props) => {
  const { openModal } = useBaseModal();

  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [minPrice, setMinPrice] = useState<number | ''>('');
  const [maxPrice, setMaxPrice] = useState<number | ''>('');
  const [scoreOption, setScoreOption] = useState('전체');

  const isPriceInitialized = useRef(false);

  useEffect(() => {
    if (isPriceInitialized.current || !priceRange) return;

    setMinPrice(priceRange.minPrice ?? '');
    setMaxPrice(priceRange.maxPrice ?? '');
    isPriceInitialized.current = true;
  }, [priceRange]);

  const categories = useMemo(() => {
    const available = new Set(items.map((item) => item.category));

    return Object.keys(CATEGORY_LABEL_MAP)
      .filter((category) => available.has(category))
      .map((category) => ({
        value: category,
        label: CATEGORY_LABEL_MAP[category],
      }));
  }, [items]);

  const toggleCategory = (category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((it) => it !== category)
        : [...prev, category]
    );
  };

  const filteredItems = useMemo(() => {
    const minScore = SCORE_THRESHOLD_MAP[scoreOption] ?? 0;

    return items.filter((item) => {
      if (
        selectedCategories.length > 0 &&
        !selectedCategories.includes(item.category)
      )
        return false;
      if (minPrice !== '' && item.price < minPrice) return false;
      if (maxPrice !== '' && item.price > maxPrice) return false;
      if (item.totalScore < minScore) return false;

      return true;
    });
  }, [items, selectedCategories, minPrice, maxPrice, scoreOption]);

  return (
    <div className="w-full h-full px-12.5 pt-12.5">
      <div className="w-full h-full flex flex-col gap-4">
        <div className="flex gap-2.5 items-center justify-start">
          {/* 제목 */}
          <span className="typo-h2_bold24">| 듀프 제품 목록</span>
          <InfoIcon
            className="size-5 text-gray-900 cursor-pointer"
            onClick={() => openModal('guideModal')}
          />
        </div>

        {/* 필터 */}
        <ResultFilter
          categories={categories}
          selectedCategories={selectedCategories}
          onToggleCategory={toggleCategory}
          minPrice={minPrice}
          maxPrice={maxPrice}
          onChangeMinPrice={setMinPrice}
          onChangeMaxPrice={setMaxPrice}
          scoreOption={scoreOption}
          onChangeScoreOption={setScoreOption}
        />

        {/* 듀프 제품 리스트 */}
        {filteredItems.length > 0 ? (
          <div className="w-full grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-y-10 overflow-y-auto pb-12.5 scrollbar-hide justify-items-center">
            {filteredItems.map((item) => (
              <DupeCard key={item.productId} item={item} />
            ))}
          </div>
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center gap-2">
            <span className="typo-body_bold16 text-gray-900">
              선택하신 조건으로 검색된 결과가 없어요.
            </span>
            <span className="typo-body_med14 text-gray-600">
              필터 조건을 조정해보세요.
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultContent;
