package dalum.dalum.domain.product.repository.projection;

import dalum.dalum.domain.product.enums.LargeCategory;

import java.util.List;
import java.util.Map;

public interface ProductCandidateProjection {
    Long getId();
    LargeCategory getLargeCategory();
    String getStyle();
    List<Double> getMaterialVector();
    List<Map<String, Object>> getDominantColors();
}