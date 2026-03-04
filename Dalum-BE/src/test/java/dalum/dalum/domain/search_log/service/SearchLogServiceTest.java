package dalum.dalum.domain.search_log.service;

import dalum.dalum.domain.dupe_product.enitty.DupeProduct;
import dalum.dalum.domain.dupe_product.repository.DupeProductRepository;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.product.converter.ProductConverter;
import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.search_log.converter.SearchLogConverter;
import dalum.dalum.domain.search_log.dto.response.SearchLogDetailResponse;
import dalum.dalum.domain.search_log.dto.response.SearchLogListResponse;
import dalum.dalum.domain.search_log.entity.SearchLog;
import dalum.dalum.domain.search_log.exception.SearchLogException;
import dalum.dalum.domain.search_log.exception.code.SearchLogErrorCode;
import dalum.dalum.domain.search_log.repository.SearchLogRepository;
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
@DisplayName("SearchLogService 테스트")
class SearchLogServiceTest {

    @Mock
    private SearchLogRepository searchLogRepository;

    @Mock
    private MemberRepository memberRepository;

    @Mock
    private LikeProductRepository likeProductRepository;

    @Mock
    private DupeProductRepository dupeProductRepository;

    @Mock
    private SearchLogConverter searchLogConverter;

    @Mock
    private ProductConverter productConverter;

    @InjectMocks
    private SearchLogServiceImpl searchLogService;

    @Test
    @DisplayName("정상적으로 검색 로그를 조회한다")
    void testGetSearchLog_Success() {
        // given
        Long memberId = 1L;
        Integer page = 1;
        Integer size = 10;

        Member member = Member.builder().id(memberId).build();
        List<SearchLog> searchLogs = new ArrayList<>();
        Page<SearchLog> searchLogPage = new PageImpl<>(searchLogs, PageRequest.of(0, 10), 0);
        SearchLogListResponse response = new SearchLogListResponse(0, 0L, new ArrayList<>());

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(searchLogRepository.findAllByMemberOrderByCreatedAtDesc(eq(member), any(PageRequest.class)))
                .thenReturn(searchLogPage);
        when(searchLogConverter.toSearchLogListResponse(searchLogPage)).thenReturn(response);

        // when
        SearchLogListResponse result = searchLogService.getSearchLog(memberId, page, size);

        // then
        assertThat(result).isNotNull();
        verify(memberRepository).findById(memberId);
        verify(searchLogRepository).findAllByMemberOrderByCreatedAtDesc(eq(member), any(PageRequest.class));
        verify(searchLogConverter).toSearchLogListResponse(searchLogPage);
    }

    @Test
    @DisplayName("페이지와 사이즈가 null일 때 기본값을 사용한다")
    void testGetSearchLog_WithNullPageAndSize() {
        // given
        Long memberId = 1L;

        Member member = Member.builder().id(memberId).build();
        List<SearchLog> searchLogs = new ArrayList<>();
        Page<SearchLog> searchLogPage = new PageImpl<>(searchLogs, PageRequest.of(0, 10), 0);
        SearchLogListResponse response = new SearchLogListResponse(0, 0L, new ArrayList<>());

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(searchLogRepository.findAllByMemberOrderByCreatedAtDesc(eq(member), any(PageRequest.class)))
                .thenReturn(searchLogPage);
        when(searchLogConverter.toSearchLogListResponse(searchLogPage)).thenReturn(response);

        // when
        SearchLogListResponse result = searchLogService.getSearchLog(memberId, null, null);

        // then
        assertThat(result).isNotNull();
        verify(searchLogRepository).findAllByMemberOrderByCreatedAtDesc(eq(member), eq(PageRequest.of(0, 10)));
    }

    @Test
    @DisplayName("페이지가 0 이하일 때 첫 번째 페이지를 조회한다")
    void testGetSearchLog_WithInvalidPage() {
        // given
        Long memberId = 1L;
        Integer page = 0;
        Integer size = 10;

        Member member = Member.builder().id(memberId).build();
        List<SearchLog> searchLogs = new ArrayList<>();
        Page<SearchLog> searchLogPage = new PageImpl<>(searchLogs, PageRequest.of(0, 10), 0);
        SearchLogListResponse response = new SearchLogListResponse(0, 0L, new ArrayList<>());

        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(searchLogRepository.findAllByMemberOrderByCreatedAtDesc(eq(member), any(PageRequest.class)))
                .thenReturn(searchLogPage);
        when(searchLogConverter.toSearchLogListResponse(searchLogPage)).thenReturn(response);

        // when
        SearchLogListResponse result = searchLogService.getSearchLog(memberId, page, size);

        // then
        assertThat(result).isNotNull();
        verify(searchLogRepository).findAllByMemberOrderByCreatedAtDesc(eq(member), eq(PageRequest.of(0, 10)));
    }

    @Test
    @DisplayName("검색 로그 상세 조회 - 성공")
    void getSearchLogDetail_Success() {
        // given
        Long memberId = 1L;
        Long searchLogId = 100L;

        Member member = Member.builder()
                .id(memberId)
                .build();

        SearchLog searchLog = SearchLog.builder()
                .id(searchLogId)
                .member(member)
                .inputImageUrl("https://example.com/image.jpg")
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

        DupeProduct dupeProduct1 = DupeProduct.builder()
                .id(1L)
                .searchLog(searchLog)
                .product(product1)
                .similarityScore(0.95)
                .build();

        DupeProduct dupeProduct2 = DupeProduct.builder()
                .id(2L)
                .searchLog(searchLog)
                .product(product2)
                .similarityScore(0.85)
                .build();

        List<DupeProduct> dupeProducts = List.of(dupeProduct1, dupeProduct2);
        List<Product> products = List.of(product1, product2);
        List<Long> productIds = List.of(1L, 2L);
        Set<Long> likeProductIds = Set.of(1L); // product1만 좋아요

        ProductDto productDto1 = ProductDto.builder()
                .productId(1L)
                .name("상품1")
                        .brand("브랜드1")
                                .price(10000)
                                .imageUrl("https://example.com/product1.jpg")
                                        .similarity(0.95)
                                        .isLiked(true)
                                        .build();

        ProductDto productDto2 = ProductDto.builder()
                .productId(2L)
                .name("상품2")
                        .brand("브랜드2")
                                .price(20000)
                                .imageUrl("https://example.com/product2.jpg")
                                        .similarity(0.85)
                                        .isLiked(false)
                                        .build();

        List<ProductDto> productDtos = List.of(productDto1, productDto2);

        SearchLogDetailResponse expectedResponse = SearchLogDetailResponse.builder()
                .searchLogId(searchLogId)
                .searchDate(LocalDateTime.now())
                .imageUrl("https://example.com/image.jpg")
                        .results(productDtos)
                        .build();

        when(searchLogRepository.findById(searchLogId)).thenReturn(Optional.of(searchLog));
        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(dupeProductRepository.findBySearchLog(searchLog)).thenReturn(dupeProducts);
        when(likeProductRepository.findLikeProductIds(memberId, productIds)).thenReturn(likeProductIds);
        when(productConverter.toProductDtoList(products, likeProductIds)).thenReturn(productDtos);
        when(searchLogConverter.toSearchLogDetailResponse(searchLog, productDtos)).thenReturn(expectedResponse);

        // when
        SearchLogDetailResponse result = searchLogService.getSearchLogDetail(memberId, searchLogId);

        // then
        assertThat(result).isNotNull();
        assertThat(result.searchLogId()).isEqualTo(searchLogId);
        assertThat(result.results()).hasSize(2);
        assertThat(result.results().get(0).isLiked()).isTrue();
        assertThat(result.results().get(1).isLiked()).isFalse();

        verify(searchLogRepository).findById(searchLogId);
        verify(memberRepository).findById(memberId);
        verify(dupeProductRepository).findBySearchLog(searchLog);
        verify(likeProductRepository).findLikeProductIds(memberId, productIds);
        verify(productConverter).toProductDtoList(products, likeProductIds);
        verify(searchLogConverter).toSearchLogDetailResponse(searchLog, productDtos);
    }

    @Test
    @DisplayName("검색 로그 상세 조회 - 검색 로그 없음 예외")
    void getSearchLogDetail_SearchLogNotFound() {
        // given
        Long memberId = 1L;
        Long searchLogId = 999L;

        when(searchLogRepository.findById(searchLogId)).thenReturn(Optional.empty());

        // when & then
        assertThatThrownBy(() -> searchLogService.getSearchLogDetail(memberId, searchLogId))
                .isInstanceOf(SearchLogException.class)
                .extracting("code")
                .isEqualTo(SearchLogErrorCode.NOT_FOUND);

        verify(searchLogRepository).findById(searchLogId);
        verify(memberRepository, never()).findById(any());
    }


    @Test
    @DisplayName("검색 로그 상세 조회 - 중복 상품 없음")

    void getSearchLogDetail_NoDupeProducts() {
        // given
        Long memberId = 1L;
        Long searchLogId = 100L;

        Member member = Member.builder()
                .id(memberId)
                .build();

        SearchLog searchLog = SearchLog.builder()
                .id(searchLogId)
                .member(member)
                .inputImageUrl("https://example.com/image.jpg")
                        .build();

        List<DupeProduct> emptyDupeProducts = Collections.emptyList();
        List<ProductDto> emptyProductDtos = Collections.emptyList();

        SearchLogDetailResponse expectedResponse = SearchLogDetailResponse.builder()
                .searchLogId(searchLogId)
                .searchDate(LocalDateTime.now())
                .imageUrl("https://example.com/image.jpg")
                        .results(emptyProductDtos)
                        .build();

        when(searchLogRepository.findById(searchLogId)).thenReturn(Optional.of(searchLog));
        when(memberRepository.findById(memberId)).thenReturn(Optional.of(member));
        when(dupeProductRepository.findBySearchLog(searchLog)).thenReturn(emptyDupeProducts);
        when(likeProductRepository.findLikeProductIds(memberId, Collections.emptyList()))
                .thenReturn(Collections.emptySet());
        when(productConverter.toProductDtoList(Collections.emptyList(), Collections.emptySet()))
                .thenReturn(emptyProductDtos);
        when(searchLogConverter.toSearchLogDetailResponse(searchLog, emptyProductDtos))
                .thenReturn(expectedResponse);

        // when
        SearchLogDetailResponse result = searchLogService.getSearchLogDetail(memberId, searchLogId);

        // then
        assertThat(result).isNotNull();
        assertThat(result.results()).isEmpty();

        verify(searchLogRepository).findById(searchLogId);
        verify(memberRepository).findById(memberId);
        verify(dupeProductRepository).findBySearchLog(searchLog);
        verify(likeProductRepository).findLikeProductIds(memberId, Collections.emptyList());
        verify(productConverter).toProductDtoList(Collections.emptyList(), Collections.emptySet());
        verify(searchLogConverter).toSearchLogDetailResponse(searchLog, emptyProductDtos);
    }

}
