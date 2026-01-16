package dalum.dalum.domain.dupe_product.repository;

import dalum.dalum.domain.dupe_product.enitty.DupeProduct;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DupeProductRepository extends JpaRepository<DupeProduct, Long> {
}
