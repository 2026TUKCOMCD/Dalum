package dalum.dalum.domain.product.converter;

import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.entity.Product;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Component
public class ProductConverter {

    public ProductDto toProductDto(Product product, boolean isLiked) {
        return ProductDto.builder()
                .productId(product.getId())
                .name(product.getProductName())
                .category(product.getLargeCategory().name())
                .brand(product.getBrand())
                .price(product.getPrice())
                .imageUrl(product.getImageUrl())
                .isLiked(isLiked)
                .build();
    }

    public List<ProductDto> toProductDtoList(List<Product> products, Set<Long> likeProductIds) {
        return products.stream()
                .map(product -> toProductDto(product, likeProductIds.contains(product.getId())))
                .collect(Collectors.toList());
    }

}
