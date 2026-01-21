package dalum.dalum.domain.search_log.service;

import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.search_log.converter.SearchLogConverter;
import dalum.dalum.domain.search_log.dto.response.SearchLogListResponse;
import dalum.dalum.domain.search_log.entity.SearchLog;
import dalum.dalum.domain.search_log.repository.SearchLogRepository;
import dalum.dalum.global.apipayload.exception.GeneralException;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class SearchLogService {

    private final SearchLogRepository searchLogRepository;
    private final MemberRepository memberRepository;

    private final SearchLogConverter searchLogConverter;

    public SearchLogListResponse getSearchLog(Long memberId, Integer page, Integer size) {
        Member member = memberRepository.findById(memberId).orElseThrow(
                () -> new GeneralException(MemberErrorCode.NOT_FOUND));

        int pageIndex = (page != null && page > 0) ? page - 1 : 0; // 페이지는 0부터 시작
        int pageSize = (size != null) ? size : 10; // 기본값은 10

        PageRequest pageRequest = PageRequest.of(pageIndex, pageSize);

        Page<SearchLog> searchLogPage = searchLogRepository.findAllByMemberOrderByCreatedAt(member, pageRequest);

        SearchLogListResponse response = searchLogConverter.toSearchLogListResponse(searchLogPage);

        return response;
    }


}
