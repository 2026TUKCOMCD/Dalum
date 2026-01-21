package dalum.dalum.domain.search_log.service;

import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.search_log.converter.SearchLogConverter;
import dalum.dalum.domain.search_log.dto.response.SearchLogListResponse;
import dalum.dalum.domain.search_log.entity.SearchLog;
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

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

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
    private SearchLogConverter searchLogConverter;

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
        when(searchLogRepository.findAllByMemberOrderByCreatedAt(eq(member), any(PageRequest.class)))
                .thenReturn(searchLogPage);
        when(searchLogConverter.toSearchLogListResponse(searchLogPage)).thenReturn(response);

        // when
        SearchLogListResponse result = searchLogService.getSearchLog(memberId, page, size);

        // then
        assertThat(result).isNotNull();
        verify(memberRepository).findById(memberId);
        verify(searchLogRepository).findAllByMemberOrderByCreatedAt(eq(member), any(PageRequest.class));
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
        when(searchLogRepository.findAllByMemberOrderByCreatedAt(eq(member), any(PageRequest.class)))
                .thenReturn(searchLogPage);
        when(searchLogConverter.toSearchLogListResponse(searchLogPage)).thenReturn(response);

        // when
        SearchLogListResponse result = searchLogService.getSearchLog(memberId, null, null);

        // then
        assertThat(result).isNotNull();
        verify(searchLogRepository).findAllByMemberOrderByCreatedAt(eq(member), eq(PageRequest.of(0, 10)));
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
        when(searchLogRepository.findAllByMemberOrderByCreatedAt(eq(member), any(PageRequest.class)))
                .thenReturn(searchLogPage);
        when(searchLogConverter.toSearchLogListResponse(searchLogPage)).thenReturn(response);

        // when
        SearchLogListResponse result = searchLogService.getSearchLog(memberId, page, size);

        // then
        assertThat(result).isNotNull();
        verify(searchLogRepository).findAllByMemberOrderByCreatedAt(eq(member), eq(PageRequest.of(0, 10)));
    }
}