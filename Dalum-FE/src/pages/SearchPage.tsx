import { useMemo, useRef, useState } from "react";
import UploadIcon from "../assets/icons/UploadIcon";
import { Button } from "../components/commons/Button";
import type { SearchDupeProductsRequest } from "../types/search/Search.types";
import { useSearchStore } from "../stores/search/searchStore";
import { useNavigate } from "react-router-dom";

const SearchPage = () => {
  const { searchDupe, isLoading } = useSearchStore();
  const navigate = useNavigate();

  const [selected, setSelected] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [brandInput, setBrandInput] = useState("");

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const priceOptions = [
    "50,000원 미만",
    "50,000원 이상 ~ 100,000원 미만",
    "100,000원 이상 ~ 200,000원 미만",
    "200,000원 이상",
    "상관 없음",
  ];

  type PriceRange = {
    minPrice?: number;
    maxPrice?: number;
  };

  const PRICE_RANGE_MAP: Record<string, PriceRange> = {
    "50,000원 미만": { maxPrice: 49999 },
    "50,000원 이상 ~ 100,000원 미만": { minPrice: 50000, maxPrice: 99999 },
    "100,000원 이상 ~ 200,000원 미만": { minPrice: 100000, maxPrice: 199999 },
    "200,000원 이상": { minPrice: 200000 },
    "상관 없음": {},
  };

  const getPriceRange = (selected: string): PriceRange =>
    PRICE_RANGE_MAP[selected] ?? {};

  // 미리보기 URL
  const previewUrl = useMemo(() => {
    if (!imageFile) return "";
    return URL.createObjectURL(imageFile);
  }, [imageFile]);

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  const onChangeFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("이미지 파일만 업로드할 수 있어요.");
      e.target.value = "";
      return;
    }

    setImageFile(file);

    e.target.value = "";
  };

  const removeImage = () => {
    setImageFile(null);
  };

  const onClickSearch = async () => {
    if (!imageFile) return;

    const priceRange = getPriceRange(selected);

    const payload: SearchDupeProductsRequest = {
      image: imageFile,
      ...(brandInput.trim() && { brand: brandInput.trim() }),
      ...priceRange,
    };

    try {
      await searchDupe(payload);
      navigate("/result");
    } catch {
      alert("듀프 제품 검색 실패");
    }
  };

  return (
    <div className="w-full h-full flex px-25 py-12.5 items-center justify-center gap-7.5">
      {/* 이미지 업로드 영역 */}
      <div className="w-full h-full flex flex-col gap-5">
        {/* 이미지 업로드 */}
        <div className="w-full h-full border border-gray-900 rounded-lg flex flex-col items-center justify-center gap-5">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={onChangeFile}
            className="hidden"
          />
          {!imageFile ? (
            <>
              <Button
                variant="gray"
                size="md"
                leftIcon={<UploadIcon className="size-4" />}
                onClick={openFilePicker}
              >
                파일 선택
              </Button>
              <span className="typo-body_med18 text-gray-800 opacity-50">
                이미지를 업로드하고 듀프 제품을 찾아보세요
              </span>
            </>
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center gap-4 p-5">
              {/* 미리보기 */}
              <img
                src={previewUrl}
                alt="업로드 미리보기"
                className="max-h-[300px] w-auto rounded-lg object-contain border border-gray-500"
              />

              <div className="w-full flex gap-2">
                <Button
                  variant="gray"
                  size="md"
                  fullWidth
                  onClick={openFilePicker}
                >
                  다른 이미지 선택
                </Button>
                <Button
                  variant="gray"
                  size="md"
                  fullWidth
                  onClick={removeImage}
                >
                  이미지 제거
                </Button>
              </div>
            </div>
          )}
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
        <div className="w-full flex flex-col gap-7.5">
          {/* 제목 */}
          <div className="flex flex-col items-start justify-center gap-3 text-gray-900">
            <span className="typo-h2_bold24">| 세부사항</span>
          </div>
          {/* 브랜드 명 입력 */}
          <div className="w-full flex flex-col gap-3">
            <span className="typo-body_bold18">| 제품 브랜드 (선택)</span>
            <input
              className="w-full bg-gray-50 text-base placeholder:font-extralight font-medium text-gray-900 px-5 py-4 rounded-lg outline-none"
              placeholder="업로드한 제품의 브랜드 명을 입력해주세요."
              value={brandInput}
              onChange={(e) => setBrandInput(e.target.value)}
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
        <Button
          variant="cta_primary"
          size="cta"
          fullWidth
          disabled={!selected || !imageFile || isLoading}
          onClick={onClickSearch}
        >
          듀프 제품 찾기
        </Button>
      </div>
    </div>
  );
};

export default SearchPage;
