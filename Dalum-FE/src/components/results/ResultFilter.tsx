import { scoreOptions } from '../../constants';

export type SortField = 'color' | 'design' | 'material';
export type SortDirection = 'asc' | 'desc';

const SORT_FIELDS: { field: SortField; label: string }[] = [
  { field: 'color', label: '색상 유사도' },
  { field: 'design', label: '디자인 유사도' },
  { field: 'material', label: '재질 유사도' },
];

type Props = {
  minPrice: number | '';
  maxPrice: number | '';
  onChangeMinPrice: (value: number | '') => void;
  onChangeMaxPrice: (value: number | '') => void;

  scoreOption: string;
  onChangeScoreOption: (option: string) => void;

  sortField: SortField | null;
  sortDirection: SortDirection | null;
  onChangeSort: (field: SortField, direction: SortDirection) => void;
};

const ResultFilter = ({
  minPrice,
  maxPrice,
  onChangeMinPrice,
  onChangeMaxPrice,
  scoreOption,
  onChangeScoreOption,
  sortField,
  sortDirection,
  onChangeSort,
}: Props) => {
  return (
    <div className="w-full flex flex-col gap-3 pb-4 border-b border-primary-600">
      {/* 점수 필터 */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="typo-body_bold12 text-gray-600 w-18 shrink-0">
          닮음 지수
        </span>
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

      {/* 유사도 정렬 */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="typo-body_bold12 text-gray-600 w-18 shrink-0">
          유사도
        </span>
        {SORT_FIELDS.flatMap(({ field, label }) =>
          (['desc', 'asc'] as const).map((direction) => {
            const isSelected =
              sortField === field && sortDirection === direction;

            return (
              <button
                key={`${field}-${direction}`}
                type="button"
                onClick={() => onChangeSort(field, direction)}
                className={`typo-body_bold12 px-3 py-1.5 rounded-full border transition-colors cursor-pointer ${
                  isSelected
                    ? 'bg-primary-900 text-gray-0 border-primary-900'
                    : 'bg-screen-0 text-gray-600 border-gray-100'
                }`}
              >
                {label} {direction === 'desc' ? '↑' : '↓'}
              </button>
            );
          })
        )}
      </div>

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
    </div>
  );
};

export default ResultFilter;
