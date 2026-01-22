package dalum.dalum.domain.search_log.repository;

import dalum.dalum.domain.dupe_product.enitty.DupeProduct;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.search_log.entity.SearchLog;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SearchLogRepository extends JpaRepository<SearchLog, Long> {

    // 검색 기록 조회
    Page<SearchLog> findAllByMemberOrderByCreatedAtDesc(Member member, Pageable pageable);

}
