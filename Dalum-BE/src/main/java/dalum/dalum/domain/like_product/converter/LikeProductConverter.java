package dalum.dalum.domain.like_product.converter;

import dalum.dalum.domain.like_product.dto.response.LikeProductListResponse;
import dalum.dalum.domain.like_product.dto.response.LikeProductResponse;
import dalum.dalum.domain.like_product.dto.response.LikeToggleResponse;
import dalum.dalum.domain.like_product.entity.LikeProduct;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class LikeProductConverter {

    public LikeToggleResponse toLikeToggleResponse(boolean liked) {
        return new LikeToggleResponse(liked);
    }

    public LikeProductResponse toLikeProductResponse(LikeProduct likeProduct) {
        return LikeProductResponse.builder()
                .productId(likeProduct.getId())
                .name(likeProduct.getProduct().getProductName())
                .discountRate(likeProduct.getProduct().getDiscountRate())
                .discountPrice(likeProduct.getProduct().getDiscountPrice())
                .imageUrl(likeProduct.getProduct().getImageUrl())
                .purchaseLink(likeProduct.getProduct().getPurchaseLink())
                .isLiked(true)
                .build();
    }

    public LikeProductListResponse toLikeProductListResponse(Page<LikeProduct> likeProducts) {
        List<LikeProductResponse> likeProductResponses = likeProducts.stream()
                .map(this::toLikeProductResponse)
                .toList();

        return LikeProductListResponse.builder()
                .totalPage(likeProducts.getTotalPages())
                .totalElements(likeProducts.getTotalElements())
                .likeProducts(likeProductResponses)
                .build();
    }
}
