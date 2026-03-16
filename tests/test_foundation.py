from app.tools.validate_target_tool import validate_target_tool
from app.tools.check_scope_tool import check_scope_tool


def run():
    target_result = validate_target_tool("target-web")
    print("validate_target_tool:", target_result)

    scope_result = check_scope_tool(
        target="target-web",
        requested_profile="baseline",
        authorization_ref="approved-local-lab",
    )
    print("check_scope_tool:", scope_result)


if __name__ == "__main__":
    run()