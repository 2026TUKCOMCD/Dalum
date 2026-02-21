import { authApi } from "../../api";
// import type { GetDupeSearchListResponse } from "../../types/me/Me.types";

// 듀프 제품 검색 기록 상세 조회 API
// const getDetailDupeSearch = async (
//   searchId: number,
// ): Promise<GetDupeSearchListResponse> => {
//   const { data } = await authApi.get<GetDupeSearchListResponse>(
//     `/api/v1/me/search-logs/${searchId}`,
//   );

//   return data;
// };

// export default getDetailDupeSearch;

const getDetailDupeSearch = async (searchId: number) => {
  const { data } = await authApi.get(`/api/v1/me/search-logs/${searchId}`);

  return data;
};

export default getDetailDupeSearch;
