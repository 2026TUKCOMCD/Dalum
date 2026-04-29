import InfoIcon from '../../assets/icons/InfoIcon';
import { dupeMockData } from '../../mocks/dupeMockData';
import useBaseModal from '../../stores/modals/baseModal';
import DupeCard from './DupeCard';

const ResultContent = () => {
  const { openModal } = useBaseModal();
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
        {/* 듀프 제품 리스트 */}
        <div className="w-full grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-y-10 gap-x-5 overflow-y-auto pb-12.5 scrollbar-hide justify-items-center">
          {dupeMockData.map((item) => (
            <DupeCard key={item.id} item={item} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultContent;
