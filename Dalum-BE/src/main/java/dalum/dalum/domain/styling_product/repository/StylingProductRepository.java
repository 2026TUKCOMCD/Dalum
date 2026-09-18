package dalum.dalum.domain.styling_product.repository;

import dalum.dalum.domain.styling.entity.Styling;
import dalum.dalum.domain.styling_product.entity.StylingProduct;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface StylingProductRepository extends JpaRepository<StylingProduct, Long> {

    List<StylingProduct> findByStyling(Styling styling);

    @Query("SELECT DISTINCT sp.product.id FROM StylingProduct sp " +
            "WHERE sp.styling.id IN :stylingIds")
    List<Long> findProductIdsByStylingIds(@Param("stylingIds") List<Long> stylingIds);
}
