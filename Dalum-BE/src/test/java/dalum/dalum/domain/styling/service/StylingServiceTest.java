package dalum.dalum.domain.styling.service;

import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.product.converter.ProductConverter;
import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.repository.ProductRepository;
import dalum.dalum.domain.styling.converter.StylingConverter;
import dalum.dalum.domain.styling.dto.response.MyStylingListResponse;
import dalum.dalum.domain.styling.dto.response.MyStylingResponse;
import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;
import dalum.dalum.domain.styling.dto.response.StylingSaveResponse;
import dalum.dalum.domain.styling.entity.Styling;
import dalum.dalum.domain.styling.repository.StylingRepository;
import dalum.dalum.domain.styling_product.repository.StylingProductRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.time.LocalDateTime;
import java.util.*;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("StylingService 테스트")
class StylingServiceTest {

    @InjectMocks
    private StylingServiceImpl stylingService; // 진짜 서비스 (여기에 가짜들을 주입)

    @Mock
    private MemberRepository memberRepository;
    @Mock
    private ProductRepository productRepository;
    @Mock
    private LikeProductRepository likeProductRepository;
    @Mock
    private StylingRepository stylingRepository;
    @Mock
    private StylingProductRepository stylingProductRepository;

    @Mock
    private ProductConverter productConverter; // 컨버터도 Mock 처리
    @Mock
    private StylingConverter stylingConverter; // 컨버터도 Mock 처리


    @Test
    @DisplayName("추천 상품 생성 성공")
    void testCreateRecommendationSuccess() {
        // Given
        Long memberId = 1L;
        Long targetProductId = 10L;

        // 가짜 객체 생성
        Member testMember = Member.builder().id(memberId).build();
        Product targetProduct = Product.builder().id(targetProductId).build();
        LikeProduct testLikeProduct = LikeProduct.builder().member(testMember).product(targetProduct).build();
        Product recommendedProduct = Product.builder().id(20L).build();

        // 1. Repository Mocking
        when(memberRepository.findById(memberId))
                .thenReturn(Optional.of(testMember));

        when(productRepository.findById(targetProductId))
                .thenReturn(Optional.of(targetProduct));

        when(likeProductRepository.findById(targetProductId))
                .thenReturn(Optional.of(testLikeProduct));

        when(productRepository.findAllById(anyList()))
                .thenReturn(List.of(recommendedProduct));

        when(likeProductRepository.findLikeProductIds(any(), anyList()))
                .thenReturn(Set.of(targetProductId));

        // 2. Converter Mocking
        ProductDto targetProductDto = ProductDto.builder().productId(targetProductId).build();
        ProductDto recommendedProductDto = ProductDto.builder().productId(20L).build();
        StylingRecommendationResponse mockResponse = StylingRecommendationResponse.builder().stylingId(100L).build();

        when(productConverter.toProductDto(eq(targetProduct), anyBoolean()))
                .thenReturn(targetProductDto);

        when(productConverter.toProductDtoList(anyList(), anySet()))
                .thenReturn(List.of(recommendedProductDto));

        when(stylingConverter.toResponse(any(Styling.class), eq(targetProductDto), anyList()))
                .thenReturn(mockResponse);

        // When
        StylingRecommendationResponse response = stylingService.createRecommendation(memberId, targetProductId);

        // Then
        assertThat(response).isNotNull();
        verify(stylingRepository, times(1)).save(any(Styling.class));
    }

    @Test
    @DisplayName("스타일링 저장 성공")
    void testSaveStylingSuccess() {
        // Given
        Long stylingId = 100L;
        Long memberId = 1L;

        Member testMember = Member.builder().id(memberId).build();
        LikeProduct testLikeProduct = LikeProduct.builder().member(testMember).build();
        Styling testStyling = Styling.builder()
                .id(stylingId)
                .member(testMember)
                .likeProduct(testLikeProduct)
                .build();

        StylingSaveResponse mockResponse = StylingSaveResponse.builder().stylingId(stylingId).build();

        // 1. Repository Mocking
        when(stylingRepository.findById(stylingId))
                .thenReturn(Optional.of(testStyling));

        // 2. Converter Mocking
        when(stylingConverter.toStylingSaveResponse(stylingId))
                .thenReturn(mockResponse);

        // When
        StylingSaveResponse response = stylingService.saveStyling(memberId, stylingId);

        // Then
        assertThat(response).isNotNull();
        assertThat(response.stylingId()).isEqualTo(stylingId);
        verify(stylingRepository, times(1)).findById(stylingId);
        verify(stylingConverter, times(1)).toStylingSaveResponse(stylingId);
    }

    @Test
    @DisplayName("내 스타일링 목록 조회 - 성공")
    void getMyStylings_Success() {
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
                .build();

        Product product2 = Product.builder()
                .id(2L)
                .productName("상품2")
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

        Styling styling1 = Styling.builder()
                .id(1L)
                .member(member)
                .likeProduct(likeProduct1)
                .isScrapped(true)
                .build();

        Styling styling2 = Styling.builder()
                .id(2L)
                .member(member)
                .likeProduct(likeProduct2)
                .isScrapped(true)
                .build();

        List<Styling> stylingList = List.of(styling1, styling2);
        Page<Styling> stylingPage = new PageImpl<>(stylingList, PageRequest.of(0, 10), 2);

        MyStylingResponse myStylingResponse1 = MyStylingResponse.builder()
                .stylingId(1L)
                .imageUrl("https://example.com/styling1.jpg")
                .createdAt(LocalDateTime.now())
                .build();

        MyStylingResponse myStylingResponse2 = MyStylingResponse.builder()
                .stylingId(2L)
                .imageUrl("https://example.com/styling2.jpg")
                .createdAt(LocalDateTime.now())
                .build();

        List<MyStylingResponse> myStylingResponses = List.of(myStylingResponse1, myStylingResponse2);

        MyStylingListResponse expectedResponse = MyStylingListResponse.builder()
                .stylings(myStylingResponses)
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(stylingRepository.findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), any(PageRequest.class)))
                .thenReturn(stylingPage);
        when(stylingConverter.toMyStylingListResponse(stylingPage)).thenReturn(expectedResponse);

        // when
        MyStylingListResponse result = stylingService.getMyStylings(memberId, page, size);

        // then
        assertThat(result).isNotNull();
        assertThat(result.stylings()).hasSize(2);
        assertThat(result.stylings().get(0).stylingId()).isEqualTo(1L);
        assertThat(result.stylings().get(1).stylingId()).isEqualTo(2L);

        verify(memberRepository).findById(memberId);
        verify(stylingRepository).findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), eq(PageRequest.of(0, 10)));
        verify(stylingConverter).toMyStylingListResponse(stylingPage);
    }

    @Test
    @DisplayName("내 스타일링 목록 조회 - 페이지와 사이즈가 null일 때 기본값 사용")
    void getMyStylings_WithNullPageAndSize() {
        // given
        Long memberId = 1L;

        Member member = Member.builder()
                .id(memberId)
                .build();

        List<Styling> emptyList = new ArrayList<>();
        Page<Styling> emptyPage = new PageImpl<>(emptyList, PageRequest.of(0, 10), 0);

        MyStylingListResponse expectedResponse = MyStylingListResponse.builder()
                .stylings(Collections.emptyList())
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(stylingRepository.findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), any(PageRequest.class)))
                .thenReturn(emptyPage);
        when(stylingConverter.toMyStylingListResponse(emptyPage)).thenReturn(expectedResponse);

        // when
        MyStylingListResponse result = stylingService.getMyStylings(memberId, null, null);

        // then
        assertThat(result).isNotNull();
        assertThat(result.stylings()).isEmpty();

        verify(memberRepository).findById(memberId);
        verify(stylingRepository).findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), eq(PageRequest.of(0, 10)));
        verify(stylingConverter).toMyStylingListResponse(emptyPage);
    }

    @Test
    @DisplayName("내 스타일링 목록 조회 - 페이지가 0 이하일 때 첫 번째 페이지 조회")
    void getMyStylings_WithInvalidPage() {
        // given
        Long memberId = 1L;
        Integer page = 0;
        Integer size = 10;

        Member member = Member.builder()
                .id(memberId)
                .build();

        List<Styling> emptyList = new ArrayList<>();
        Page<Styling> emptyPage = new PageImpl<>(emptyList, PageRequest.of(0, 10), 0);

        MyStylingListResponse expectedResponse = MyStylingListResponse.builder()
                .stylings(Collections.emptyList())
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(stylingRepository.findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), any(PageRequest.class)))
                .thenReturn(emptyPage);
        when(stylingConverter.toMyStylingListResponse(emptyPage)).thenReturn(expectedResponse);

        // when
        MyStylingListResponse result = stylingService.getMyStylings(memberId, page, size);

        // then
        assertThat(result).isNotNull();

        verify(memberRepository).findById(memberId);
        verify(stylingRepository).findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), eq(PageRequest.of(0, 10)));
        verify(stylingConverter).toMyStylingListResponse(emptyPage);
    }

    @Test
    @DisplayName("내 스타일링 목록 조회 - 저장된 스타일링이 없는 경우")
    void getMyStylings_EmptyStylings() {
        // given
        Long memberId = 1L;
        Integer page = 1;
        Integer size = 10;

        Member member = Member.builder()
                .id(memberId)
                .build();

        List<Styling> emptyList = Collections.emptyList();
        Page<Styling> emptyPage = new PageImpl<>(emptyList, PageRequest.of(0, 10), 0);

        MyStylingListResponse expectedResponse = MyStylingListResponse.builder()
                .stylings(Collections.emptyList())
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(stylingRepository.findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), any(PageRequest.class)))
                .thenReturn(emptyPage);
        when(stylingConverter.toMyStylingListResponse(emptyPage)).thenReturn(expectedResponse);

        // when
        MyStylingListResponse result = stylingService.getMyStylings(memberId, page, size);

        // then
        assertThat(result).isNotNull();
        assertThat(result.stylings()).isEmpty();

        verify(memberRepository).findById(memberId);
        verify(stylingRepository).findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), eq(PageRequest.of(0, 10)));
        verify(stylingConverter).toMyStylingListResponse(emptyPage);
    }

    @Test
    @DisplayName("내 스타일링 목록 조회 - 커스텀 페이지 사이즈")
    void getMyStylings_WithCustomPageSize() {
        // given
        Long memberId = 1L;
        Integer page = 2;
        Integer size = 5;

        Member member = Member.builder()
                .id(memberId)
                .build();

        List<Styling> emptyList = new ArrayList<>();
        Page<Styling> emptyPage = new PageImpl<>(emptyList, PageRequest.of(1, 5), 0);

        MyStylingListResponse expectedResponse = MyStylingListResponse.builder()
                .stylings(Collections.emptyList())
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(stylingRepository.findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), any(PageRequest.class)))
                .thenReturn(emptyPage);
        when(stylingConverter.toMyStylingListResponse(emptyPage)).thenReturn(expectedResponse);

        // when
        MyStylingListResponse result = stylingService.getMyStylings(memberId, page, size);

        // then
        assertThat(result).isNotNull();

        verify(memberRepository).findById(memberId);
        verify(stylingRepository).findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), eq(PageRequest.of(1, 5)));
        verify(stylingConverter).toMyStylingListResponse(emptyPage);
    }

    @Test
    @DisplayName("내 스타일링 목록 조회 - isScrapped가 true인 것만 조회")
    void getMyStylings_OnlyScrappedStylings() {
        // given
        Long memberId = 1L;
        Integer page = 1;
        Integer size = 10;

        Member member = Member.builder()
                .id(memberId)
                .build();

        Product product = Product.builder()
                .id(1L)
                .productName("상품1")
                .build();

        LikeProduct likeProduct = LikeProduct.builder()
                .id(1L)
                .member(member)
                .product(product)
                .build();

        // isScrapped가 true인 스타일링만 있어야 함
        Styling scrappedStyling = Styling.builder()
                .id(1L)
                .member(member)
                .likeProduct(likeProduct)
                .isScrapped(true)
                .build();

        List<Styling> stylingList = List.of(scrappedStyling);
        Page<Styling> stylingPage = new PageImpl<>(stylingList, PageRequest.of(0, 10), 1);

        MyStylingResponse myStylingResponse = MyStylingResponse.builder()
                .stylingId(1L)
                .imageUrl("https://example.com/styling1.jpg")
                .createdAt(LocalDateTime.now())
                .build();

        MyStylingListResponse expectedResponse = MyStylingListResponse.builder()
                .stylings(List.of(myStylingResponse))
                .build();

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(stylingRepository.findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), any(PageRequest.class)))
                .thenReturn(stylingPage);
        when(stylingConverter.toMyStylingListResponse(stylingPage)).thenReturn(expectedResponse);

        // when
        MyStylingListResponse result = stylingService.getMyStylings(memberId, page, size);

        // then
        assertThat(result).isNotNull();
        assertThat(result.stylings()).hasSize(1);
        assertThat(result.stylings().get(0).stylingId()).isEqualTo(1L);

        // isScrapped가 true인 것만 조회하는 메서드가 호출되었는지 확인
        verify(stylingRepository).findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(eq(memberId), any(PageRequest.class));
    }
}
