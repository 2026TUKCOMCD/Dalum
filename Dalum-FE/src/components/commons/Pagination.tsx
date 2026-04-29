import ChevronLeftIcon from '../../assets/icons/ChevronLeftIcon';
import ChevronRightIcon from '../../assets/icons/ChevronRightIcon';

export type PaginationProps = {
  total: number; // 전체 개수
  current: number; // 현재 index
  onChange: (index: number) => void;
};

const Pagination = ({ total, current, onChange }: PaginationProps) => {
  const handlePrev = () => {
    onChange((current - 1 + total) % total);
  };

  const handleNext = () => {
    onChange((current + 1) % total);
  };

  return (
    <div className="w-fit flex items-center justify-center gap-2">
      {/* 이전 */}
      <div
        className="flex items-center justify-center p-2 cursor-pointer"
        onClick={handlePrev}
      >
        <ChevronLeftIcon className="size-4 text-primary-900" />
      </div>

      {/* 페이지 번호 */}
      <div className="flex items-center justify-center gap-1 typo-body_med16">
        {Array.from({ length: total }).map((_, i) => (
          <span
            key={i}
            onClick={() => onChange(i)}
            className={`
              flex items-center justify-center rounded-full w-8 h-8 cursor-pointer
              ${
                i === current
                  ? 'bg-primary-900 text-gray-0'
                  : 'text-primary-900'
              }
            `}
          >
            {i + 1}
          </span>
        ))}
      </div>

      {/* 다음 */}
      <div
        className="flex items-center justify-center p-2 cursor-pointer"
        onClick={handleNext}
      >
        <ChevronRightIcon className="size-4 text-primary-900" />
      </div>
    </div>
  );
};

export default Pagination;
