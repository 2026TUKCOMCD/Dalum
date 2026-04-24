import { authApi } from '../../api';
import type { SaveStylingResponse } from '../../types/stylings/Styling.types';

// 스타일링 저장 API
const saveStyling = async (stylingId: number): Promise<SaveStylingResponse> => {
  const { data } = await authApi.post<SaveStylingResponse>(
    `/api/v1/stylings/${stylingId}/save`,
    null,
    { params: { stylingId } }
  );

  return data;
};

export default saveStyling;
