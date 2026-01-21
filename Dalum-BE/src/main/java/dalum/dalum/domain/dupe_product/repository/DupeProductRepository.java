package dalum.dalum.domain.dupe_product.repository;

import dalum.dalum.domain.dupe_product.enitty.DupeProduct;
import dalum.dalum.domain.search_log.entity.SearchLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DupeProductRepository extends JpaRepository<DupeProduct, Long> {

    List<DupeProduct> findBySearchLog(SearchLog searchLog);
}
