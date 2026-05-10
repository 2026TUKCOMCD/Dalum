import CloseIcon from '../../assets/icons/CloseIcon';
import useBaseModal from '../../stores/modals/baseModal';
import type { DetailDupeSearchItem } from '../../types/me/Me.types';
import SimilarityChart from '../results/SimilarityChart';
import SimilarityGauge from '../results/SimilarityGauge';

const SimilarityCheckModal = () => {
  const { closeModal, modalProps } = useBaseModal();
  const { item } = modalProps as { item: DetailDupeSearchItem };

  const similarityData = [
    {
      name: '색상',
      value: Number((item.colorScore * 100).toFixed(1)),
      color: '#8F9DC5',
    },
    {
      name: '재질',
      value: Number((item.materialScore * 100).toFixed(1)),
      color: '#4B61A1',
    },
    {
      name: '디자인',
      value: Number((item.designScore * 100).toFixed(1)),
      color: '#D2D8E8',
    },
  ];

  const totalScore = Number((item.totalScore * 100).toFixed(1));

  return (
    <div className="w-fit flex flex-col gap-7.5 p-7.5 items-center justify-center bg-screen-default rounded-[14px]">
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
      <div className="w-full flex items-center justify-between gap-10">
        {/* 차트 영역 */}
        <div className="w-67.5 h-67.5">
          <SimilarityChart data={similarityData} />
        </div>
        {/* 닮음지수 영역 */}
        <div className="w-fit h-67.5 flex flex-col items-center justify-between py-2">
          <SimilarityGauge score={totalScore} />
          <div className="flex flex-col gap-1 items-start justify-center">
            <span className="typo-body_med12 text-gray-900">닮음 지수란,</span>
            <span className="typo-body_thin12 text-gray-900">
              사용자가 업로드한 이미지와 사용자가 선택한 듀프 제품 간의
              <br />
              색상, 재질, 디자인 유사도를 평균치로 계산한 점수입니다.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimilarityCheckModal;
