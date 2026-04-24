import type React from 'react';
import { priceOptions } from '../../constants';

type Props = {
  brandInput: string;
  setBrandInput: React.Dispatch<React.SetStateAction<string>>;

  selected: string;
  setSelected: React.Dispatch<React.SetStateAction<string>>;
};

const SearchCondition = ({
  brandInput,
  setBrandInput,
  selected,
  setSelected,
}: Props) => {
  return (
    <div className="w-full flex flex-col items-start">
      <div className="w-full flex flex-col gap-6">
        {/* 제목 */}
        <div className="flex flex-col items-start justify-center gap-3 text-gray-900">
          <span className="typo-h2_bold24">| 세부사항</span>
        </div>
        {/* 브랜드 명 입력 */}
        <div className="w-full flex flex-col gap-3">
          <span className="typo-body_bold16">| 제품 브랜드 (선택)</span>
          <input
            className="w-full bg-gray-50 text-xs placeholder:font-extralight font-medium text-gray-900 px-5 py-4 rounded-sm outline-none"
            placeholder="업로드한 제품의 브랜드 명을 입력해주세요."
            value={brandInput}
            onChange={(e) => setBrandInput(e.target.value)}
          />
          <span className="typo-body_thin12 text-gray-900">
            · 입력한 브랜드는 추천 결과에서 제외됩니다. <br />· 제외할 브랜드가
            없다면 ‘없음’ 혹은 ‘-’을 입력해주세요
          </span>
        </div>
        {/* 희망 가격대 선택 */}
        <div className="flex flex-col gap-3">
          <span className="typo-body_bold16">| 희망 제품 가격대</span>

          {priceOptions.map((option) => {
            const isChecked = selected === option;

            return (
              <label
                key={option}
                className="relative flex items-center gap-2 cursor-pointer select-none"
              >
                <input
                  type="radio"
                  name="price"
                  value={option}
                  checked={isChecked}
                  onChange={(e) => setSelected(e.target.value)}
                  className="absolute left-0 top-0 h-4 w-4 opacity-0"
                />

                {/* 커스텀 라디오 버튼 */}
                <span
                  className={`flex h-4 w-4 items-center justify-center rounded-full border transition-all ${isChecked ? 'border-primary-900' : 'border-gray-900'}`}
                >
                  <span
                    className={`h-2 w-2 rounded-full transition-all ${isChecked ? 'bg-primary-900' : 'bg-transparent'}`}
                  />
                </span>

                {/* 가격 라벨 */}
                <span
                  className={`transition-colors ${isChecked ? 'text-primary-900 typo-body_bold12' : 'text-gray-900 typo-body_thin12'}`}
                >
                  {option}
                </span>
              </label>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SearchCondition;
