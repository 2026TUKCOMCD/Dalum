package dalum.dalum.domain.dupe_product.enitty;

import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.search_log.entity.SearchLog;
import dalum.dalum.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@NoArgsConstructor(access = lombok.AccessLevel.PROTECTED)
@AllArgsConstructor
@Getter
@Builder
public class DupeProduct extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "dupe_product_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "search_log_id", nullable = false)
    private SearchLog searchLog;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    @Column(name = "rank", nullable = false)
    private Integer rank;

    @Column(name = "similarity_score", nullable = false)
    private Double similarityScore;

    @Column(name = "color_score")
    private Double colorScore;

    @Column(name = "material_score")
    private Double materialScore;

    @Column(name = "design_score")
    private Double designScore;

}
