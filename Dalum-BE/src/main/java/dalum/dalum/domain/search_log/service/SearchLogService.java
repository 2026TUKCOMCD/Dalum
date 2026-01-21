package dalum.dalum.domain.search_log.service;

import dalum.dalum.domain.search_log.dto.response.SearchLogDetailResponse;
import dalum.dalum.domain.search_log.dto.response.SearchLogListResponse;

public interface SearchLogService {

    public SearchLogListResponse getSearchLog(Long memberId, Integer page, Integer size);

    public SearchLogDetailResponse getSearchLogDetail(Long memberId, Long searchLogId);


}
