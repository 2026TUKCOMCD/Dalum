package dalum.dalum.domain.styling.service;

import dalum.dalum.domain.styling.dto.response.StylingSaveResponse;
import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;

public interface StylingService {

    public StylingRecommendationResponse createRecommendation(Long memberId, Long targetProductId);

    public StylingSaveResponse saveStyling(Long memberId, Long stylingId);

}
