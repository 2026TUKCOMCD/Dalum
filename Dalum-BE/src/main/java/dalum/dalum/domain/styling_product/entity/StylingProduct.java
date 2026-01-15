package dalum.dalum.domain.styling_product.entity;

import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.styling.entity.Styling;
import dalum.dalum.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Getter
@Builder
public class StylingProduct extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "styling_id", nullable = false)
    private Styling styling;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    public void setStyling(Styling styling) {
        this.styling = styling;
    }
}
