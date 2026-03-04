package dalum.dalum.domain.search_log.exception;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import dalum.dalum.global.apipayload.exception.GeneralException;

public class SearchLogException extends GeneralException {
    public SearchLogException(BaseErrorCode code) {
        super(code);
    }
}
