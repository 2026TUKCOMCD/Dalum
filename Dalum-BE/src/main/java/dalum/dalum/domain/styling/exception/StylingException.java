package dalum.dalum.domain.styling.exception;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import dalum.dalum.global.apipayload.exception.GeneralException;

public class StylingException extends GeneralException {
    public StylingException(BaseErrorCode code) {
        super(code);
    }
}
