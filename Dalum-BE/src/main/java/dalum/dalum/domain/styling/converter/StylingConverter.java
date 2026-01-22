package dalum.dalum.domain.styling.converter;

import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.styling.dto.response.*;
import dalum.dalum.domain.styling.entity.Styling;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Component
public class StylingConverter {

    // 스타일링 추천
    public StylingRecommendationResponse toResponse(Styling styling, ProductDto mainItem, List<ProductDto> subItems) {

        // 1. Stream으로 카테고리별 그룹핑
        Map<String, List<ProductDto>> groupedMap = subItems.stream()
                .collect(Collectors.groupingBy(ProductDto::category));

        // 2. Map을 List<RecommendationCategoryDto>로 변환
        List<RecommendationCategoryResponse> recommendations = groupedMap.entrySet().stream()
                .map(entry -> RecommendationCategoryResponse.builder()
                        .category(entry.getKey())
                        .products(entry.getValue())
                        .build())
                .collect(Collectors.toList());

        // 3. 최종 응답 생성
        return StylingRecommendationResponse.builder()
                .stylingId(styling.getId())
                .mainItem(mainItem)
                .resultItems(recommendations)
                .build();
    }

    public StylingSaveResponse toStylingSaveResponse(Long stylingId) {
        return StylingSaveResponse.builder()
                .stylingId(stylingId)
                .build();
    }

    public MyStylingResponse toMyStylingResponse(Styling styling) {

        String targetImageUrl = "";

        // NullPointerException 방지
        if (styling.getLikeProduct() != null && styling.getLikeProduct().getProduct() != null) {
            targetImageUrl = styling.getLikeProduct().getProduct().getImageUrl();
        }

        return MyStylingResponse.builder()
                .stylingId(styling.getId())
                .imageUrl(targetImageUrl)
                .createdAt(styling.getCreatedAt())
                .build();
    }

    public MyStylingListResponse toMyStylingListResponse(Page<Styling> stylingPage) {

        List<MyStylingResponse> myStylinglist = stylingPage.stream().
                map(this::toMyStylingResponse).toList();

        return MyStylingListResponse.builder()
                .stylings(myStylinglist)
                .build();
    }

    // 상세 조회용 변환기
    public MyStylingDetailResponse toMyStylingDetailResponse(
            Styling styling,
            Product mainProduct,
            boolean isMainLiked,
            List<MyStylingDetailResponse.RecommendedItemDetail> recommendedItems
    ) {

        // 스타일링 이름은 날짜로
        String stylingName = styling.getCreatedAt().toLocalDate() + " 추천 스타일링";

        // 메인 상품 DTO 변환
        MyStylingDetailResponse.MainProductDetail mainProductDetail =
                MyStylingDetailResponse.MainProductDetail.builder()
                        .productId(mainProduct.getId())
                        .name(mainProduct.getProductName())
                        .brand(mainProduct.getBrand())
                        .discountRate(mainProduct.getDiscountRate())
                        .discountPrice(mainProduct.getDiscountPrice())
                        .imageUrl(mainProduct.getImageUrl())
                        .purchaseLink(mainProduct.getPurchaseLink())
                        .isLiked(isMainLiked)
                        .build();
        // 최종 변환
        return MyStylingDetailResponse.builder()
                .stylingId(styling.getId())
                .createdAt(styling.getCreatedAt())
                .name(stylingName)
                .mainProduct(mainProductDetail)
                .items(recommendedItems)
                .build();
    }

    // 추천 아이템 단일 변환
    public MyStylingDetailResponse.RecommendedItemDetail toRecommendItemDetailResponse(
            Product product,
            boolean isLiked
    ) {
        return MyStylingDetailResponse.RecommendedItemDetail.builder()
                .productId(product.getId())
                .category(product.getLargeCategory())
                .name(product.getProductName())
                .brand(product.getBrand())
                .discountRate(product.getDiscountRate())
                .discountPrice(product.getDiscountPrice())
                .imageUrl(product.getImageUrl())
                .purchaseLink(product.getPurchaseLink())
                .isLiked(isLiked)
                .build();
    }


}