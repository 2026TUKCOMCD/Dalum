package dalum.dalum.domain.search_log.converter;

import dalum.dalum.domain.search_log.dto.response.SearchLogListResponse;
import dalum.dalum.domain.search_log.dto.response.SearchLogResponse;
import dalum.dalum.domain.search_log.entity.SearchLog;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.stream.Collectors;

@Component
public class SearchLogConverter {

    public SearchLogResponse toSearchLogResponse(SearchLog searchLog) {
        return SearchLogResponse.builder()
                .searchLogId(searchLog.getId())
                .inputImageUrl(searchLog.getInputImageUrl())
                .searchTime(searchLog.getCreatedAt())
                .build();
    }

    public SearchLogListResponse toSearchLogListResponse(Page<SearchLog> searchLogPage) {
        List<SearchLogResponse> searchLogResponses = searchLogPage.stream()
                .map(this::toSearchLogResponse)
                .collect(Collectors.toList());

        return SearchLogListResponse.builder()
                .totalPage(searchLogPage.getTotalPages())
                .totalElements(searchLogPage.getTotalElements())
                .searchLogs(searchLogResponses)
                .build();


    }

}
