package dalum.dalum.domain.like_product.service;

import dalum.dalum.domain.like_product.converter.LikeProductConverter;
import dalum.dalum.domain.like_product.dto.response.LikeProductListResponse;
import dalum.dalum.domain.like_product.dto.response.LikeProductResponse;
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
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("LikeProductService - getLikeProducts 테스트")
class LikeProductServiceTest {

    @Mock
    private LikeProductRepository likeProductRepository;

    @Mock
    private MemberRepository memberRepository;

    @Mock
    private ProductRepository productRepository;

    @Mock
    private LikeProductConverter likeProductConverter;

    @InjectMocks
    private LikeProductService likeProductService;

    @Test
    @DisplayName("좋아요 목록 조회 - 성공")
    void getLikeProducts_Success() {
        // given
        Long memberId = 1L;
        Integer page = 1;
        Integer size = 10;

        Member member = Member.builder()
                .id(memberId)
                .build();

        Product product1 = Product.builder()
                .id(1L)
                .productName("상품1")
                .brand("브랜드1")
                .price(10000)
                .imageUrl("https://example.com/product1.jpg")
                .build();

        Product product2 = Product.builder()
                .id(2L)
                .productName("상품2")
                .brand("브랜드2")
                .price(20000)
                .imageUrl("https://example.com/product2.jpg")
                .build();

        LikeProduct likeProduct1 = LikeProduct.builder()
                .id(1L)
                .member(member)
                .product(product1)
                .build();

        LikeProduct likeProduct2 = LikeProduct.builder()
                .id(2L)
                .member(member)
                .product(product2)
                .build();

        List<LikeProduct> likeProductList = List.of(likeProduct1, likeProduct2);
        Page<LikeProduct> likeProductPage = new PageImpl<>(likeProductList, PageRequest.of(0, 10), 2);

        LikeProductResponse likeProductResponse1 = LikeProductResponse.builder()
                .productId(1L)
                .name("상품1")
                .discountRate(0.1)
                .discountPrice(9000)
                .imageUrl("https://example.com/product1.jpg")
                .purchaseLink("https://example.com/buy1")
                .isLiked(true)
                .build();

        LikeProductResponse likeProductResponse2 = LikeProductResponse.builder()
                .productId(2L)
                .name("상품2")
                .discountRate(0.2)
                .discountPrice(16000)
                .imageUrl("https://example.com/product2.jpg")
                .purchaseLink("https://example.com/buy2")
                .isLiked(true)
                .build();

        List<LikeProductResponse> likeProductResponses = List.of(likeProductResponse1, likeProductResponse2);

        LikeProductListResponse expectedResponse = LikeProductListResponse.builder()
                .totalPage(1)
                .totalElements(2L)
                .likeProducts(likeProductResponses)
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(likeProductRepository.findAllByMemberOrderByCreatedAtDesc(eq(member), any(PageRequest.class)))
                .thenReturn(likeProductPage);
        when(likeProductConverter.toLikeProductListResponse(likeProductPage)).thenReturn(expectedResponse);

        // when
        LikeProductListResponse result = likeProductService.getLikeProducts(memberId, page, size);

        // then
        assertThat(result).isNotNull();
        assertThat(result.totalPage()).isEqualTo(1);
        assertThat(result.totalElements()).isEqualTo(2L);
        assertThat(result.likeProducts()).hasSize(2);
        assertThat(result.likeProducts().get(0).isLiked()).isTrue();
        assertThat(result.likeProducts().get(1).isLiked()).isTrue();

        verify(memberRepository).findById(memberId);
        verify(likeProductRepository).findAllByMemberOrderByCreatedAtDesc(eq(member), eq(PageRequest.of(0, 10)));
        verify(likeProductConverter).toLikeProductListResponse(likeProductPage);
    }


    @Test
    @DisplayName("좋아요 목록 조회 - 페이지와 사이즈가 null일 때 기본값 사용")
    void getLikeProducts_WithNullPageAndSize() {
        // given
        Long memberId = 1L;

        Member member = Member.builder()
                .id(memberId)
                .build();

        List<LikeProduct> emptyList = new ArrayList<>();
        Page<LikeProduct> emptyPage = new PageImpl<>(emptyList, PageRequest.of(0, 10), 0);

        LikeProductListResponse expectedResponse = LikeProductListResponse.builder()
                .totalPage(0)
                .totalElements(0L)
                .likeProducts(Collections.emptyList())
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(likeProductRepository.findAllByMemberOrderByCreatedAtDesc(eq(member), any(PageRequest.class)))
                .thenReturn(emptyPage);
        when(likeProductConverter.toLikeProductListResponse(emptyPage)).thenReturn(expectedResponse);

        // when
        LikeProductListResponse result = likeProductService.getLikeProducts(memberId, null, null);

        // then
        assertThat(result).isNotNull();
        assertThat(result.likeProducts()).isEmpty();

        verify(memberRepository).findById(memberId);
        verify(likeProductRepository).findAllByMemberOrderByCreatedAtDesc(eq(member), eq(PageRequest.of(0, 10)));
        verify(likeProductConverter).toLikeProductListResponse(emptyPage);
    }

    @Test
    @DisplayName("좋아요 목록 조회 - 페이지가 0 이하일 때 첫 번째 페이지 조회")
    void getLikeProducts_WithInvalidPage() {
        // given
        Long memberId = 1L;
        Integer page = 0;
        Integer size = 10;

        Member member = Member.builder()
                .id(memberId)
                .build();

        List<LikeProduct> emptyList = new ArrayList<>();
        Page<LikeProduct> emptyPage = new PageImpl<>(emptyList, PageRequest.of(0, 10), 0);

        LikeProductListResponse expectedResponse = LikeProductListResponse.builder()
                .totalPage(0)
                .totalElements(0L)
                .likeProducts(Collections.emptyList())
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(likeProductRepository.findAllByMemberOrderByCreatedAtDesc(eq(member), any(PageRequest.class)))
                .thenReturn(emptyPage);
        when(likeProductConverter.toLikeProductListResponse(emptyPage)).thenReturn(expectedResponse);

        // when
        LikeProductListResponse result = likeProductService.getLikeProducts(memberId, page, size);

        // then
        assertThat(result).isNotNull();

        verify(memberRepository).findById(memberId);
        verify(likeProductRepository).findAllByMemberOrderByCreatedAtDesc(eq(member), eq(PageRequest.of(0, 10)));
        verify(likeProductConverter).toLikeProductListResponse(emptyPage);
    }

    @Test
    @DisplayName("좋아요 목록 조회 - 좋아요한 상품이 없는 경우")
    void getLikeProducts_EmptyLikeProducts() {
        // given
        Long memberId = 1L;
        Integer page = 1;
        Integer size = 10;

        Member member = Member.builder()
                .id(memberId)
                .build();

        List<LikeProduct> emptyList = Collections.emptyList();
        Page<LikeProduct> emptyPage = new PageImpl<>(emptyList, PageRequest.of(0, 10), 0);

        LikeProductListResponse expectedResponse = LikeProductListResponse.builder()
                .totalPage(0)
                .totalElements(0L)
                .likeProducts(Collections.emptyList())
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(likeProductRepository.findAllByMemberOrderByCreatedAtDesc(eq(member), any(PageRequest.class)))
                .thenReturn(emptyPage);
        when(likeProductConverter.toLikeProductListResponse(emptyPage)).thenReturn(expectedResponse);

        // when
        LikeProductListResponse result = likeProductService.getLikeProducts(memberId, page, size);

        // then
        assertThat(result).isNotNull();
        assertThat(result.totalPage()).isEqualTo(0);
        assertThat(result.totalElements()).isEqualTo(0L);
        assertThat(result.likeProducts()).isEmpty();

        verify(memberRepository).findById(memberId);
        verify(likeProductRepository).findAllByMemberOrderByCreatedAtDesc(eq(member), eq(PageRequest.of(0, 10)));
        verify(likeProductConverter).toLikeProductListResponse(emptyPage);
    }

    @Test
    @DisplayName("좋아요 목록 조회 - 커스텀 페이지 사이즈")
    void getLikeProducts_WithCustomPageSize() {
        // given
        Long memberId = 1L;
        Integer page = 2;
        Integer size = 5;

        Member member = Member.builder()
                .id(memberId)
                .build();

        List<LikeProduct> emptyList = new ArrayList<>();
        Page<LikeProduct> emptyPage = new PageImpl<>(emptyList, PageRequest.of(1, 5), 0);

        LikeProductListResponse expectedResponse = LikeProductListResponse.builder()
                .totalPage(0)
                .totalElements(0L)
                .likeProducts(Collections.emptyList())
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(likeProductRepository.findAllByMemberOrderByCreatedAtDesc(eq(member), any(PageRequest.class)))
                .thenReturn(emptyPage);
        when(likeProductConverter.toLikeProductListResponse(emptyPage)).thenReturn(expectedResponse);

        // when
        LikeProductListResponse result = likeProductService.getLikeProducts(memberId, page, size);

        // then
        assertThat(result).isNotNull();

        verify(memberRepository).findById(memberId);
        verify(likeProductRepository).findAllByMemberOrderByCreatedAtDesc(eq(member), eq(PageRequest.of(1, 5)));
        verify(likeProductConverter).toLikeProductListResponse(emptyPage);
    }
}
