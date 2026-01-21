package dalum.dalum.domain.search_log.dto.response;

import lombok.Builder;
import lombok.NoArgsConstructor;

import java.util.List;

@Builder
public record SearchLogListResponse(
        int totalPage,
        long totalElements,
        List<SearchLogResponse> searchLogs
) {
}
