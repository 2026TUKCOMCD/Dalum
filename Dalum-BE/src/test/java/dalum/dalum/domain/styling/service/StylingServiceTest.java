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
import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;
import dalum.dalum.domain.styling.entity.Styling;
import dalum.dalum.domain.styling.repository.StylingRepository;
import dalum.dalum.domain.styling_product.repository.StylingProductRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;
import java.util.Set;

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

}