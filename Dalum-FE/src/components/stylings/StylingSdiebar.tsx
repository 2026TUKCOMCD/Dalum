import HomeIcon from '../../assets/icons/HomeIcon';
import RefreshIcon from '../../assets/icons/RefreshIcon';
import SaveIcon from '../../assets/icons/SaveIcon';
import { useStylingStore } from '../../stores/stylings/stylingStore';
import { Button } from '../commons/Button';
import SidebarStylingCard from './SidebarStylingCard';

const StylingSidebar = () => {
  const { stylingResult } = useStylingStore();

  const mainItem = stylingResult?.mainItem;

  return (
    <div className="h-full w-fit flex flex-col items-start justify-start px-12.5 py-12.5 border-r border-gray-600">
      <div className="flex flex-col gap-5">
        {/* 제목 */}
        <span className="typo-h2_bold24 text-gray-900">| 좋아요한 제품</span>
        {/* 업로드 이미지 */}
        {mainItem && <SidebarStylingCard item={mainItem} />}

        {/* 버튼 영역 */}
        <div className="flex flex-col gap-2.5">
          {/* 버튼 */}
          <Button
            variant="primary"
            size="lg"
            fullWidth
            leftIcon={<SaveIcon className="size-4" />}
            onClick={() => {
              // openModal("dupeResearchModal");
            }}
          >
            스타일링 저장
          </Button>
          <Button
            variant="primary"
            size="lg"
            fullWidth
            leftIcon={<RefreshIcon className="size-4" />}
            // onClick={() => navigate("/my")}
          >
            다른 스타일링 추천
          </Button>
          <Button
            variant="primary"
            size="lg"
            fullWidth
            leftIcon={<HomeIcon className="size-4" />}
            // onClick={() => navigate("/my")}
          >
            마이 페이지로 이동
          </Button>
        </div>
      </div>
    </div>
  );
};

export default StylingSidebar;
