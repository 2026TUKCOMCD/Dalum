package dalum.dalum.domain.product.repository;

import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.repository.projection.ProductCandidateProjection;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Long> {

    // 네이티브 쿼리로 조회 — material_vector/dominant_colors를 JPA 컨버터로 파싱하지 않고
    // raw JSON 문자열 그대로 받아서 AI 서버로 그대로 전달 (불필요한 파싱 ↔ 직렬화 왕복 제거)
    @Query(value = "SELECT product_id AS id, large_category AS largeCategory, style AS style, " +
            "material_vector AS materialVectorJson, dominant_colors AS dominantColorsJson " +
            "FROM product " +
            "WHERE large_category IN (:categories) AND product_id NOT IN (:excludeIds) " +
            "AND material_vector IS NOT NULL " +
            "AND (style IS NULL OR style IN (:compatibleStyles)) " +
            "LIMIT :limit",
            nativeQuery = true)
    List<ProductCandidateProjection> findCandidates(@Param("categories") List<String> categories,
                                                    @Param("excludeIds") List<Long> excludeIds,
                                                    @Param("compatibleStyles") List<String> compatibleStyles,
                                                    @Param("limit") int limit);

}
