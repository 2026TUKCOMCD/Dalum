package dalum.dalum.domain.search_log.exception.code;

import dalum.dalum.global.apipayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum SearchLogSuccessCode implements BaseSuccessCode {
    OK(HttpStatus.OK,
            "SEARCH_LOG_200_1",
            "검색기록을 성공적으로 조회하였습니다."),
    DETAIL_OK(HttpStatus.OK,
            "SEARCH_LOG_200_2",
            "검색기록 상세를 성공적으로 조회하였습니다.");
    private final HttpStatus status;
    private final String code;
    private final String message;
}
