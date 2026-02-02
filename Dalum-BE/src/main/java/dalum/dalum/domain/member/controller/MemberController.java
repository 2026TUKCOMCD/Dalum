package dalum.dalum.domain.member.controller;

import dalum.dalum.domain.member.dto.response.MemberInfoResponse;
import dalum.dalum.domain.member.exception.code.MemberSuccessCode;
import dalum.dalum.domain.member.service.MemberService;
import dalum.dalum.global.apipayload.ApiResult;
import dalum.dalum.global.security.SecurityUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Tag(name = "Member", description = "회원 관련 API")
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class MemberController {

    private final MemberService memberService;

    @Operation(summary = "내 정보 조회 API", description = "로그인한 회원의 정보를 조회합니다. (마이페이지 상단용)")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "MEMBER_200_1", description = "회원을 정상적으로 조회했습니다."),
            @ApiResponse(responseCode = "MEMBER_404_1", description = "해당 유저를 찾지 못했습니다."),
    })
    @GetMapping("/members/me")
    public ApiResult<MemberInfoResponse> getMyInfo(
    ) {

        Long memberId = SecurityUtil.getCurrentMemberId();

        MemberInfoResponse response = memberService.getMemberResponse(memberId);

        return ApiResult.success(MemberSuccessCode.OK, response);

    }
}
