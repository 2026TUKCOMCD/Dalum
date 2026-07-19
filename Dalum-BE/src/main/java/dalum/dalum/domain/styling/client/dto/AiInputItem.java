package dalum.dalum.domain.styling.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

public record AiInputItem(
        @JsonProperty("material_vector") List<Double> materialVector,
        @JsonProperty("dominant_colors") List<Map<String, Object>> dominantColors,
        @JsonProperty("style") String style,
        @JsonProperty("category") String category
) {
}
