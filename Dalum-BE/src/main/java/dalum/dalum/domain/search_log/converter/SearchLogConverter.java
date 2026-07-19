package dalum.dalum.domain.search_log.converter;

import dalum.dalum.domain.dupe_product.dto.response.DupeProductDto;
import dalum.dalum.domain.dupe_product.enitty.DupeProduct;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.search_log.dto.response.SearchConditionDto;
import dalum.dalum.domain.search_log.dto.response.SearchLogDetailResponse;
import dalum.dalum.domain.search_log.dto.response.SearchLogListResponse;
import dalum.dalum.domain.search_log.dto.response.SearchLogResponse;
import dalum.dalum.domain.search_log.entity.SearchLog;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Set;
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

    public DupeProductDto toDupeProductDto(DupeProduct dp, Set<Long> likeProductIds) {
        Product product = dp.getProduct();
        return DupeProductDto.builder()
                .productId(product.getId())
                .name(product.getProductName())
                .brand(product.getBrand())
                .category(product.getLargeCategory().name())
                .discountRate(product.getDiscountRate())
                .price(product.getPrice())
                .imageUrl(product.getImageUrl())
                .purchaseUrl(product.getPurchaseLink())
                .isLiked(likeProductIds.contains(product.getId()))
                .colorScore(dp.getColorScore())
                .materialScore(dp.getMaterialScore())
                .designScore(dp.getDesignScore())
                .totalScore(dp.getSimilarityScore())
                .build();
    }

    public SearchLogDetailResponse toSearchLogDetailResponse(SearchLog searchLog, List<DupeProductDto> products) {
        SearchConditionDto conditions = this.searchConditionDto(searchLog);
        return SearchLogDetailResponse.builder()
                .searchLogId(searchLog.getId())
                .searchDate(searchLog.getCreatedAt())
                .brand(searchLog.getBrand())
                .imageUrl(searchLog.getInputImageUrl())
                .conditions(conditions)
                .results(products)
                .build();
    }

}
