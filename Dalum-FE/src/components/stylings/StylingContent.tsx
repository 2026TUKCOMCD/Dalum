import Pagination from "../commons/Pagination";
import StylingCardList from "./StylingCardList";

const StylingContent = () => {
  return (
    <div className="w-full h-full py-12.5 px-12.5 flex flex-col items-center justify-between gap-12.5">
      <div className="w-full h-full items-center justify-center">
        <StylingCardList />
      </div>
      <Pagination />
    </div>
  );
};

export default StylingContent;
