package dalum.dalum.domain.auth.exception.code;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum AuthErrorCode implements BaseErrorCode {
    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR,
            "AUTH_500_1",
            "(서버오류) 네이버 토큰 발급 실패입니다.")
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;

}
