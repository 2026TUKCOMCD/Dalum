import ChevronLeftIcon from "../../assets/icons/ChevronLeftIcon";
import ChevronRightIcon from "../../assets/icons/ChevronRightIcon";

const Pagination = () => {
  return (
    <div className="w-fit flex items-center justify-center gap-2">
      <div className="flex items-center justify-center p-2">
        <ChevronLeftIcon className="size-4  text-gray-900" />
      </div>
      <div className="flex items-center justify-center gap-1 typo-body_med16">
        <span className="flex items-center justify-center rounded-full bg-gray-900 text-gray-0 w-8 h-8">
          1
        </span>
        <span className="flex items-center justify-center rounded-full bg-none text-gray-900 w-8 h-8">
          2
        </span>
        <span className="flex items-center justify-center rounded-full bg-none text-gray-900 w-8 h-8">
          3
        </span>
        <span className="flex items-center justify-center rounded-full bg-none text-gray-900 w-8 h-8">
          4
        </span>
        <span className="flex items-center justify-center rounded-full bg-none text-gray-900 w-8 h-8">
          5
        </span>
      </div>
      <div className="flex items-center justify-center p-2">
        <ChevronRightIcon className="size-4  text-gray-900" />
      </div>
    </div>
  );
};

export default Pagination;
