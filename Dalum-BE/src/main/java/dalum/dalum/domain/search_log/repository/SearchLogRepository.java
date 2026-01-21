package dalum.dalum.domain.search_log.repository;

import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.search_log.entity.SearchLog;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SearchLogRepository extends JpaRepository<SearchLog, Long> {

    // 검색 기록 조회
    Page<SearchLog> findAllByMemberOrderByCreatedAt(Member member, Pageable pageable);
}
