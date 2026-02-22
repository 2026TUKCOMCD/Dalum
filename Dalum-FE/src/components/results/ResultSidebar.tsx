import { useNavigate } from 'react-router-dom';
import HomeIcon from '../../assets/icons/HomeIcon';
import ImageIcon from '../../assets/icons/ImageIcon';
import useBaseModal from '../../stores/modals/baseModal';
import { Button } from '../commons/Button';

type Props = {
  imageUrl?: string;
};

const ResultSidebar = ({ imageUrl }: Props) => {
  const { openModal } = useBaseModal();
  const navigate = useNavigate();

  return (
    <div className="h-full w-fit flex flex-col items-start justify-start px-7.5 py-12.5 border-r border-gray-600">
      <div className="flex flex-col gap-4">
        {/* 제목 */}
        <span className="typo-h2_bold24 text-gray-900">| 업로드 이미지</span>
        {/* 업로드 이미지 */}
        <div className="w-60 h-60 justify-center items-center flex">
          <img
            alt="업로드 이미지"
            src={imageUrl}
            className="w-full h-auto rounded-sm bg-center"
          />
        </div>

        {/* 버튼 영역 */}
        <div className="flex flex-col gap-2.5">
          {/* 버튼 */}
          <Button
            variant="primary"
            size="lg"
            fullWidth
            leftIcon={<ImageIcon className="size-4" />}
            onClick={() => {
              openModal('dupeResearchModal');
            }}
          >
            다른 이미지로 검색
          </Button>
          <Button
            variant="primary"
            size="lg"
            fullWidth
            leftIcon={<HomeIcon className="size-4" />}
            onClick={() => navigate('/my')}
          >
            마이 페이지로 이동
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ResultSidebar;
