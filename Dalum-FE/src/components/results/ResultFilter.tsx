import { scoreOptions } from '../../constants';

type Props = {
  categories: { value: string; label: string }[];
  selectedCategories: string[];
  onToggleCategory: (category: string) => void;

  minPrice: number | '';
  maxPrice: number | '';
  onChangeMinPrice: (value: number | '') => void;
  onChangeMaxPrice: (value: number | '') => void;

  scoreOption: string;
  onChangeScoreOption: (option: string) => void;
};

const ResultFilter = ({
  categories,
  selectedCategories,
  onToggleCategory,
  minPrice,
  maxPrice,
  onChangeMinPrice,
  onChangeMaxPrice,
  scoreOption,
  onChangeScoreOption,
}: Props) => {
  const isAllCategory = selectedCategories.length === 0;

  return (
    <div className="w-full flex flex-col gap-3 pb-4 border-b border-primary-600">
      {/* 카테고리 필터 */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="typo-body_bold12 text-gray-600 w-14 shrink-0">
          카테고리
        </span>
        <button
          type="button"
          onClick={() =>
            selectedCategories.forEach((category) =>
              onToggleCategory(category)
            )
          }
          className={`typo-body_bold12 px-3 py-1.5 rounded-full border transition-colors cursor-pointer ${
            isAllCategory
              ? 'bg-primary-900 text-gray-0 border-primary-900'
              : 'bg-screen-0 text-gray-600 border-gray-100'
          }`}
        >
          전체
        </button>
        {categories.map(({ value, label }) => {
          const isSelected = selectedCategories.includes(value);

          return (
            <button
              key={value}
              type="button"
              onClick={() => onToggleCategory(value)}
              className={`typo-body_bold12 px-3 py-1.5 rounded-full border transition-colors cursor-pointer ${
                isSelected
                  ? 'bg-primary-900 text-gray-0 border-primary-900'
                  : 'bg-screen-0 text-gray-600 border-gray-100'
              }`}
            >
              {label}
            </button>
          );
        })}
      </div>

      {/* 가격 & 점수 필터 */}
      <div className="flex flex-wrap items-center gap-6">
        {/* 가격 필터 */}
        <div className="flex items-center gap-2">
          <span className="typo-body_bold12 text-gray-600 w-14 shrink-0">
            가격
          </span>
          <input
            type="number"
            min={0}
            value={minPrice}
            onChange={(e) =>
              onChangeMinPrice(
                e.target.value === '' ? '' : Number(e.target.value)
              )
            }
            placeholder="최소"
            className="w-24 bg-gray-50 text-xs placeholder:font-extralight font-medium text-gray-900 px-3 py-2 rounded-sm outline-none"
          />
          <span className="typo-body_med12 text-gray-600">~</span>
          <input
            type="number"
            min={0}
            value={maxPrice}
            onChange={(e) =>
              onChangeMaxPrice(
                e.target.value === '' ? '' : Number(e.target.value)
              )
            }
            placeholder="최대"
            className="w-24 bg-gray-50 text-xs placeholder:font-extralight font-medium text-gray-900 px-3 py-2 rounded-sm outline-none"
          />
          <span className="typo-body_med12 text-gray-600">원</span>
        </div>

        {/* 점수 필터 */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="typo-body_bold12 text-gray-600">닮음 지수</span>
          {scoreOptions.map((option) => {
            const isSelected = scoreOption === option;

            return (
              <button
                key={option}
                type="button"
                onClick={() => onChangeScoreOption(option)}
                className={`typo-body_bold12 px-3 py-1.5 rounded-full border transition-colors cursor-pointer ${
                  isSelected
                    ? 'bg-primary-900 text-gray-0 border-primary-900'
                    : 'bg-screen-0 text-gray-600 border-gray-100'
                }`}
              >
                {option}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ResultFilter;
