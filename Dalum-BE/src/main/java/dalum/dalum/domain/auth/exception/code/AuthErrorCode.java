package dalum.dalum.domain.auth.exception.code;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum AuthErrorCode implements BaseErrorCode {
    INVALID_TOKEN(HttpStatus.UNAUTHORIZED,
            "AUTH_401_1",
            "유효하지 않은 토큰입니다."),
    EXPIRED_TOKEN(HttpStatus.UNAUTHORIZED,
            "AUTH_401_2",
            "만료된 토큰입니다."),
    NOT_FOUND(HttpStatus.NOT_FOUND,
            "AUTH_404_1",
            "유효하지 않은 리프레시 토큰입니다."),
    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR,
            "AUTH_500_1",
            "(서버오류) 네이버 토큰 발급 실패입니다.")
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;

}
