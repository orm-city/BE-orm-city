import subprocess
from .models import CodeSubmission, CodeSubmissionRecord
import os


# 채점 인터페이스
class CodeJudgeInterface:
    """
    코드 채점 인터페이스.
    각 언어별 채점 로직은 이 인터페이스를 구현해야 함.
    """

    def run_code(
        self, code: str, input_data: str, time_limit: int, memory_limit: int
    ) -> str:
        raise NotImplementedError("이 메서드는 서브클래스에서 구현되어야 합니다.")


# 파이썬 코드 채점 로직
class PythonCodeJudge(CodeJudgeInterface):
    def run_code(
        self, code: str, input_data: str, time_limit: int, memory_limit: int
    ) -> str:
        """
        파이썬 코드를 실행하고, Windows와 리눅스 환경에 따라 분기 처리.
        리눅스에서는 메모리 제한을 적용하고, Windows에서는 메모리 제한을 생략.
        """
        try:
            if os.name == "nt":
                result = subprocess.run(
                    ["python", "-c", code],  # Windows 환경일 경우 'python'으로 변경
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=time_limit,
                )
            else:
                import resource

                def set_memory_limit():
                    resource.setrlimit(
                        resource.RLIMIT_AS,
                        (memory_limit * 1024 * 1024, memory_limit * 1024 * 1024),
                    )

                result = subprocess.run(
                    ["python3", "-c", code],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=time_limit,
                    preexec_fn=set_memory_limit,
                )

            # 디버깅을 위해 실행 결과를 로그에 출력
            stdout = result.stdout.strip()
            stderr = result.stderr.strip() if result.stderr else "No errors"
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")

            if result.stderr:
                return f"실행 에러: {stderr}"

            return stdout

        except subprocess.TimeoutExpired:
            return "시간 초과"
        except Exception as e:
            print(f"실행 에러: {e}")
            return f"실행 에러: {e}"


# 자바스크립트 코드 채점 로직
class JavaScriptCodeJudge(CodeJudgeInterface):
    def run_code(
        self, code: str, input_data: str, time_limit: int, memory_limit: int
    ) -> str:
        """
        자바스크립트(Node.js) 코드를 실행하고, Windows와 리눅스 환경에 따라 분기 처리.
        리눅스에서는 메모리 제한을 적용하고, Windows에서는 메모리 제한을 생략.
        """
        try:
            # 제출된 자바스크립트 코드를 임시 파일로 저장
            with open("temp.js", "w") as f:
                f.write(code)

            # Windows에서는 메모리 제한 없이 실행
            if os.name == "nt":
                result = subprocess.run(
                    ["node", "temp.js"],
                    input=input_data.encode(),
                    capture_output=True,
                    text=True,
                    timeout=time_limit,
                )
            else:
                # 리눅스 환경에서 메모리 제한 적용
                import resource

                def set_memory_limit():
                    # 메모리 제한을 byte 단위로 설정 (1MB = 1024 * 1024 bytes)
                    resource.setrlimit(
                        resource.RLIMIT_AS,
                        (memory_limit * 1024 * 1024, memory_limit * 1024 * 1024),
                    )

                result = subprocess.run(
                    ["node", "temp.js"],
                    input=input_data.encode(),
                    capture_output=True,
                    text=True,
                    timeout=time_limit,
                    preexec_fn=set_memory_limit,  # 리눅스에서만 메모리 제한 적용
                )

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            return "시간 초과"
        except Exception as e:
            return f"실행 에러: {e}"


# 언어별 채점 클래스를 반환하는 팩토리 클래스
class CodeJudgeFactory:
    """
    프로그래밍 언어에 따른 코드 채점 클래스 인스턴스를 반환하는 팩토리 클래스.
    """

    @staticmethod
    def get_judge(language: str) -> CodeJudgeInterface:
        if language == "python":
            return PythonCodeJudge()
        elif language == "javascript":
            return JavaScriptCodeJudge()
        else:
            raise ValueError(f"지원하지 않는 언어입니다: {language}")


# 코드 채점을 위한 서비스 함수
def evaluate_code_submission(
    code_submission: CodeSubmission,
    submitted_code: str,
    user,
    time_limit: int,
    memory_limit: int,
) -> dict:
    """
    제출된 코드를 채점하고 결과를 반환하는 함수.
    time_limit과 memory_limit을 추가로 받아 채점 시 적용.
    """
    # 언어에 맞는 채점 클래스를 가져옴
    judge = CodeJudgeFactory.get_judge(code_submission.language)

    # 테스트 케이스 준비
    test_cases = [(code_submission.example_input, code_submission.example_output)]

    # 제출된 코드를 실행하고 결과 확인
    results = []
    all_passed = True

    for input_data, expected_output in test_cases:
        actual_output = judge.run_code(
            code=submitted_code,
            input_data=input_data,
            time_limit=time_limit,
            memory_limit=memory_limit,
        )
        passed = actual_output == expected_output
        results.append(
            {
                "input": input_data,
                "expected": expected_output,
                "actual": actual_output,
                "passed": passed,
            }
        )
        if not passed:
            all_passed = False

    # 제출 기록 저장
    CodeSubmissionRecord.objects.create(
        user=user,
        code_submission=code_submission,
        submitted_code=submitted_code,
        test_results=str(results),
        is_passed=all_passed,
    )

    return {"all_passed": all_passed, "results": results}
