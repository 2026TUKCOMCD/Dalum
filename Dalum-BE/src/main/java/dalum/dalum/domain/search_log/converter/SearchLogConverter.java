package dalum.dalum.domain.search_log.converter;

import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.search_log.dto.response.SearchConditionDto;
import dalum.dalum.domain.search_log.dto.response.SearchLogDetailResponse;
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

    public SearchConditionDto searchConditionDto(SearchLog searchLog) {
        return SearchConditionDto.builder()
                .minPrice(searchLog.getMinPrice())
                .maxPrice(searchLog.getMaxPrice())
                .build();
    }

    public SearchLogDetailResponse toSearchLogDetailResponse(SearchLog searchLog, List<ProductDto> products) {
        SearchConditionDto conditions = this.searchConditionDto(searchLog);
        return SearchLogDetailResponse.builder()
                .searchLogId(searchLog.getId())
                .searchDate(searchLog.getCreatedAt())
                .imageUrl(searchLog.getInputImageUrl())
                .conditions(conditions)
                .results(products)
                .build();
    }

}
