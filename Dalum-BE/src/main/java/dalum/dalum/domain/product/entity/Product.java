package dalum.dalum.domain.product.entity;

import dalum.dalum.domain.product.enums.LargeCategory;
import dalum.dalum.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class Product extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "product_id")
    private Long id;

    @Column(name = "shopping_mall", nullable = false)
    private String shoppingMall;

    // 대분류, 중분류, 소분류는 어느정도 정형화된다 싶으면 enum으로 바꾸는 것을 고려
    @Enumerated(EnumType.STRING)
    @Column(name = "large_category", nullable = false)
    private LargeCategory largeCategory;

    @Column(name = "medium_category", nullable = false)
    private String mediumCategory;

    @Column(name = "small_category", nullable = false)
    private String smallCategory;

    @Column(name = "product_name", nullable = false)
    private String productName;

    @Column(name = "brand", nullable = false)
    private String brand;

    @Column(name = "price", nullable = false)
    private Integer price;

    @Column(name = "discount_price", nullable = false)
    private Integer discountPrice;

    // 할인율을 정수로 주는게 프론트측에서 편할 것 같아 정수로 설정
    @Column(name = "discount_rate", nullable = false)
    private Double discountRate;

    @Column(name = "purchase_link", nullable = false, columnDefinition = "TEXT")
    private String purchaseLink;

    @Column(name = "image_url", nullable = false, columnDefinition = "TEXT")
    private String imageUrl;

}
