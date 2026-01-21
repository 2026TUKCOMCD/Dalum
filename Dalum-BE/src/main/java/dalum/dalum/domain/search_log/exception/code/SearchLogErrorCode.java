package dalum.dalum.domain.search_log.exception.code;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum SearchLogErrorCode implements BaseErrorCode {
    NOT_FOUND(HttpStatus.NOT_FOUND,
            "SEARCH_LOG_404_1",
            "해당 검색기록을 찾지 못했습니다."),
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;


}
