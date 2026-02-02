package dalum.dalum.domain.styling.repository;

import dalum.dalum.domain.styling.entity.Styling;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StylingRepository extends JpaRepository<Styling, Long> {

    // MemberId 일치 AND 좋아요한 상품만 조회
    Page<Styling> findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(Long memberId, Pageable pageable);

    void deleteByMemberId(Long memberId);
}
