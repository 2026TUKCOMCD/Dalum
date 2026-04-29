package dalum.dalum.domain.styling.converter;

import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.styling.dto.response.*;
import dalum.dalum.domain.styling.entity.Styling;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class StylingConverter {

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
                        .category(mainProduct.getLargeCategory())
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

    // 메인 상품 단일 변환
    public MyStylingDetailResponse.MainProductDetail toMainProductDetailResponse(
            Product product,
            boolean isLiked
    ) {
        return MyStylingDetailResponse.MainProductDetail.builder()
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