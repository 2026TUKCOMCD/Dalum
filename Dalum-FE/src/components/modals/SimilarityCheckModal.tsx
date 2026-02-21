import CloseIcon from '../../assets/icons/CloseIcon';
import useBaseModal from '../../stores/modals/baseModal';
import SimilarityChart from '../results/SimilarityChart';
import SimilarityGauge from '../results/SimilarityGauge';

const data = [
  { name: '색상', value: 76.3, color: '#8F9DC5' },
  { name: '재질', value: 94.3, color: '#4B61A1' },
  { name: '형태', value: 73.1, color: '#D2D8E8' },
];

const SimilarityCheckModal = () => {
  const { closeModal } = useBaseModal();

  return (
    <div className="w-175 flex flex-col gap-7.5 p-7.5 items-center justify-center bg-screen-default rounded-[14px]">
      {/* 닫기 버튼 */}
      <div className="w-full px-1 flex items-center justify-end">
        <CloseIcon
          className="size-6 cursor-pointer text-gray-900"
          onClick={() => {
            closeModal();
          }}
        />
      </div>
      {/* 컨텐츠 */}
      <div className="w-full flex items-center justify-between">
        {/* 차트 영역 */}
        <div className="w-fit h-fit">
          <SimilarityChart data={data} />
        </div>
        {/* 닮음지수 영역 */}
        <div className="w-fit h-67.5 flex flex-col items-center justify-between py-2">
          <SimilarityGauge score={73.4} />
          <div className="flex flex-col gap-1 items-start justify-center">
            <span className="typo-body_med12 text-gray-900">닮음 지수란,</span>
            <span className="typo-body_thin12 text-gray-900">
              사용자가 업로드한 이미지와 사용자가 선택한 듀프 제품 간의
              <br />
              색상, 재질, 형태 유사도를 평균치로 계산한 점수입니다.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimilarityCheckModal;
