package dalum.dalum.domain.member.controller;

import dalum.dalum.domain.member.dto.response.MemberInfoResponse;
import dalum.dalum.domain.member.exception.code.MemberSuccessCode;
import dalum.dalum.domain.member.service.MemberService;
import dalum.dalum.global.apipayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class MemberController {

    private final MemberService memberService;

    @Operation(summary = "내 정보 조회 API", description = "로그인한 회원의 정보를 조회합니다. (마이페이지 상단용)")
    @GetMapping("/members/me")
    public ApiResponse<MemberInfoResponse> getMyInfo(
            Long memberId
    ) {

        memberId = memberId == null ? 1 : memberId;

        MemberInfoResponse response = memberService.getMemberResponse(memberId);

        return ApiResponse.success(MemberSuccessCode.OK, response);

    }
}
