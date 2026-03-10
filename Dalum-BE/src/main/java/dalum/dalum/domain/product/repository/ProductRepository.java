package dalum.dalum.domain.product.repository;

import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.enums.LargeCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Long> {

    @Query("SELECT p FROM Product p WHERE p.largeCategory IN :categories AND p.id != :excludeId AND p.materialVector IS NOT NULL")
    List<Product> findCandidates(@Param("categories") List<LargeCategory> categories, @Param("excludeId") Long excludeId,
                                 @Param("compatibleStyles") List<String> compatibleStyles);

}
