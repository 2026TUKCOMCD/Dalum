package dalum.dalum.domain.product.repository;

import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.enums.LargeCategory;
import dalum.dalum.domain.product.repository.projection.ProductCandidateProjection;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Long> {

    @Query(value = "SELECT p.product_id AS id, p.large_category AS largeCategory, p.style AS style, p.material_vector AS materialVector, p.dominant_colors AS dominantColors " +
            "FROM product p " +
            "WHERE p.large_category IN :categories AND p.id != :excludeId AND p.material_vector IS NOT NULL " +
            "AND (p.style IS NULL OR p.style IN :compatibleStyles) " +
            "ORDER BY RANDOM() LIMIT :limit",
            nativeQuery = true)
    List<ProductCandidateProjection> findCandidates(@Param("categories") List<String> categories,
                                                    @Param("excludeId") Long excludeId,
                                                    @Param("compatibleStyles") List<String> compatibleStyles,
                                                    @Param("limit") int limit);

}