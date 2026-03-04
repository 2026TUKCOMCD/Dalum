package dalum.dalum.domain.dupe_product.exception;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import dalum.dalum.global.apipayload.exception.GeneralException;

public class DupeProductException extends GeneralException {
    public DupeProductException(BaseErrorCode code) {
        super(code);
    }
}
