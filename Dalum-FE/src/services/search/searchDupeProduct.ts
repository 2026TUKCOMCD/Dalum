import { authApi } from "../../api";
import { toFormData } from "../../utils";
import type {
  SearchDupeProductsRequest,
  SearchDupeProductsResponse,
} from "../../types/search/Search.types";

// 듀프 제품 검색 API
const searchDupeProducts = async (
  req: SearchDupeProductsRequest,
): Promise<SearchDupeProductsResponse> => {
  const formData = toFormData(req);

  const { data } = await authApi.post<SearchDupeProductsResponse>(
    "/api/v1/search/dupe",
    formData,
  );

  return data;
};

export default searchDupeProducts;
