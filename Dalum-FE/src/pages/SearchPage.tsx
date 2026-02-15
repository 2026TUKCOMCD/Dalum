import { useState } from "react";
import UploadIcon from "../assets/icons/UploadIcon";
import { Button } from "../components/commons/Button";

const SearchPage = () => {
  const [selected, setSelected] = useState("");

  const priceOptions = [
    "30,000원 미만",
    "30,000원 이상 ~ 50,000원 미만",
    "50,000원 이상 ~ 100,000원 미만",
    "100,000원 이상 ~ 200,000원 미만",
    "200,000원 이상",
    "상관 없음",
  ];
  return (
    <div className="w-full h-full flex px-25 py-12.5 items-center justify-center gap-7.5">
      {/* 이미지 업로드 영역 */}
      <div className="w-full h-full flex flex-col gap-5">
        {/* 이미지 업로드 */}
        <div className="w-full h-full border border-gray-900 rounded-lg flex flex-col items-center justify-center gap-5">
          <Button
            variant="gray"
            size="md"
            leftIcon={<UploadIcon className="size-4" />}
          >
            파일 선택
          </Button>
          <span className="typo-body_med18 text-gray-800 opacity-50">
            이미지를 업로드하고 듀프 제품을 찾아보세요
          </span>
        </div>
        {/* 설명 */}
        <div className="typo-body_thin14 flex flex-col justify-center items-start">
          <span>· 제품 이미지는 최대 1장만 업로드 가능합니다.</span>
          <span>
            · 제품 외의 영역이 적을수록 더 높은 유사도를 지닌 제품을 추천 받을
            수 있습니다.
          </span>
          <span>
            · 검색 결과로 제공되는 제품은 매일 00:00을 기준으로 업데이트 됩니다.
          </span>
        </div>
      </div>

      {/* 구분선 */}
      <div className="h-full border-[0.5px] border-dashed border-gray-900"></div>

      {/* 조건 설정 영역 */}
      <div className="w-full h-full flex flex-col items-start justify-between">
        <div className="flex flex-col gap-7.5">
          {/* 제목 */}
          <div className="flex flex-col items-start justify-center gap-3 text-gray-900">
            <span className="typo-h2_bold24">| 세부사항</span>
            <span className="typo-body_thin14">
              세부 사항은 듀프 제품 추천의 정확도와 고객 만족도를 높이기 위한
              정보입니다. <br />
              모든 항목을 입력하지 않아도 되지만, 자세히 입력할수록 더
              만족스러운 추천을 받을 수 있어요.
            </span>
          </div>
          {/* 브랜드 명 입력 */}
          <div className="flex flex-col gap-3">
            <span className="typo-body_bold18">| 제품 브랜드 (선택)</span>
            <input
              className="w-full bg-gray-50 text-base placeholder:font-extralight font-medium text-gray-900 px-5 py-4 rounded-lg outline-none"
              placeholder="업로드한 제품의 브랜드 명을 입력해주세요."
            />
            <span className="typo-body_thin14">
              · 입력한 브랜드는 추천 결과에서 제외됩니다. <br />· 제외할
              브랜드가 없다면 ‘없음’ 혹은 ‘-’을 입력해주세요
            </span>
          </div>
          {/* 희망 가격대 선택 */}
          <div className="flex flex-col gap-3">
            <span className="typo-body_bold18">| 희망 제품 가격대</span>

            {priceOptions.map((option) => {
              const isChecked = selected === option;

              return (
                <label
                  key={option}
                  className="flex items-center gap-2 cursor-pointer select-none"
                >
                  <input
                    type="radio"
                    name="price"
                    value={option}
                    checked={isChecked}
                    onChange={(e) => setSelected(e.target.value)}
                    className="sr-only"
                  />

                  {/* 커스텀 라디오 버튼 */}
                  <span
                    className={`flex h-4 w-4 items-center justify-center rounded-full border transition-all ${isChecked ? "border-primary-900" : "border-gray-900"}`}
                  >
                    <span
                      className={`h-2 w-2 rounded-full transition-all ${isChecked ? "bg-primary-900" : "bg-transparent"}`}
                    />
                  </span>

                  {/* 가격 라벨 */}
                  <span
                    className={`transition-colors ${isChecked ? "text-primary-900 typo-body_bold16" : "text-gray-900 typo-body_thin16"}`}
                  >
                    {option}
                  </span>
                </label>
              );
            })}
          </div>
        </div>
        {/* CTA */}
        <Button variant="primary" size="cta" fullWidth disabled={!selected}>
          듀프 제품 찾기
        </Button>
      </div>
    </div>
  );
};

export default SearchPage;
