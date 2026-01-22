package dalum.dalum.domain.styling_product.repository;

import dalum.dalum.domain.styling.entity.Styling;
import dalum.dalum.domain.styling_product.entity.StylingProduct;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface StylingProductRepository extends JpaRepository<StylingProduct, Long> {

    List<StylingProduct> findByStyling(Styling styling);
}
