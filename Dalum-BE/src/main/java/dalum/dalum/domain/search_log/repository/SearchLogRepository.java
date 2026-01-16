package dalum.dalum.domain.search_log.repository;

import dalum.dalum.domain.search_log.entity.SearchLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SearchLogRepository extends JpaRepository<SearchLog, Long> {
}
