package dalum.dalum.domain.like_product.service;

import dalum.dalum.domain.like_product.dto.response.LikeToggleResponse;
import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.exception.MemberException;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.repository.ProductRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class) // Mockito 사용 선언
class LikeProductServiceTest {

    @InjectMocks
    private LikeProductService likeProductService; // 가짜 객체들이 주입될 진짜 서비스

    @Mock
    private LikeProductRepository likeProductRepository;
    @Mock
    private MemberRepository memberRepository;
    @Mock
    private ProductRepository productRepository;

    @Test
    @DisplayName("좋아요 등록 성공: 기존에 좋아요가 없을 때 -> 저장되고 true 반환")
    void toggleLike_Register() {
        // given
        Long memberId = 1L;
        Long productId = 100L;

        Member member = Member.builder().id(memberId).build(); // 테스트용 가짜 멤버
        Product product = Product.builder().id(productId).build(); // 테스트용 가짜 상품

        // 가짜 행동 정의 (Stubbing)
        given(memberRepository.findById(memberId)).willReturn(Optional.of(member));
        given(productRepository.findById(productId)).willReturn(Optional.of(product));
        // 핵심: DB 찾아봤는데 없다고 가정!
        given(likeProductRepository.findByMemberAndProduct(member, product)).willReturn(Optional.empty());

        // when
        LikeToggleResponse response = likeProductService.toggleLike(memberId, productId);

        // then
        assertThat(response.isLiked()).isTrue(); // 결과가 true여야 함
        verify(likeProductRepository, times(1)).save(any(LikeProduct.class)); // save가 1번 호출되었는지 검증
        verify(likeProductRepository, times(0)).delete(any(LikeProduct.class)); // delete는 호출되면 안 됨
    }

    @Test
    @DisplayName("좋아요 취소 성공: 기존에 좋아요가 있을 때 -> 삭제되고 false 반환")
    void toggleLike_Cancel() {
        // given
        Long memberId = 1L;
        Long productId = 100L;

        Member member = Member.builder().id(memberId).build();
        Product product = Product.builder().id(productId).build();
        LikeProduct likeProduct = LikeProduct.builder().member(member).product(product).build();

        given(memberRepository.findById(memberId)).willReturn(Optional.of(member));
        given(productRepository.findById(productId)).willReturn(Optional.of(product));
        // 핵심: DB 찾아봤는데 이미 있다고 가정!
        given(likeProductRepository.findByMemberAndProduct(member, product)).willReturn(Optional.of(likeProduct));

        // when
        LikeToggleResponse response = likeProductService.toggleLike(memberId, productId);

        // then
        assertThat(response.isLiked()).isFalse(); // 결과가 false여야 함
        verify(likeProductRepository, times(1)).delete(likeProduct); // delete가 1번 호출되었는지 검증
        verify(likeProductRepository, times(0)).save(any(LikeProduct.class)); // save는 호출되면 안 됨
    }

    @Test
    @DisplayName("실패: 존재하지 않는 회원이 요청하면 예외 발생")
    void toggleLike_Fail_MemberNotFound() {
        // given
        Long memberId = 999L;
        Long productId = 100L;

        given(memberRepository.findById(memberId)).willReturn(Optional.empty()); // 회원 없음

        // when & then
        assertThrows(MemberException.class, () -> {
            likeProductService.toggleLike(memberId, productId);
        });
    }
}