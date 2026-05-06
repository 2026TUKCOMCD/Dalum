package dalum.dalum.global.ai;

public record AiDupeResult(
        Long productId,
        Double colorScore,
        Double materialScore,
        Double designScore,
        Double totalScore
) {
}
