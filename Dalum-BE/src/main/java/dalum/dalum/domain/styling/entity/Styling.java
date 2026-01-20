package dalum.dalum.domain.styling.entity;
import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.styling_product.entity.StylingProduct;
import dalum.dalum.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.ColumnDefault;

import java.util.ArrayList;
import java.util.List;

@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Getter
@Builder
public class Styling extends BaseEntity {

    @Id
    @GeneratedValue
    private Long id;

    @ColumnDefault("false")
    private boolean isScrapped;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "like_product_id", nullable = false)
    private LikeProduct likeProduct;

    @OneToMany(mappedBy = "styling", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<StylingProduct> stylingProducts = new ArrayList<>();

    public void addStylingProduct(StylingProduct stylingProduct) {
        stylingProducts.add(stylingProduct);
        stylingProduct.setStyling(this);
    }
}
