package dalum.dalum.domain.auth.exception;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import dalum.dalum.global.apipayload.exception.GeneralException;

public class AuthException extends GeneralException {
    public AuthException(BaseErrorCode code) {
        super(code);
    }
}
