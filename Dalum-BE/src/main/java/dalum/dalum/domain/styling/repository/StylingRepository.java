package dalum.dalum.domain.styling.repository;

import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.styling.entity.Styling;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface StylingRepository extends JpaRepository<Styling, Long> {

    // MemberId 일치 AND 좋아요한 상품만 조회
    Page<Styling> findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(Long memberId, Pageable pageable);

    void deleteByMemberId(Long memberId);

    void deleteByLikeProduct(LikeProduct likeProduct);

    // 같은 상품에 대한 최근 스타일링 id들 (최근 N번 중복 추천 방지용, N은 Pageable로 제한)
    @Query("SELECT s.id FROM Styling s " +
            "WHERE s.member.id = :memberId AND s.likeProduct.product.id = :targetProductId " +
            "ORDER BY s.createdAt DESC")
    List<Long> findRecentStylingIds(@Param("memberId") Long memberId,
                                     @Param("targetProductId") Long targetProductId,
                                     Pageable pageable);
}
