import os
import subprocess

from .models import CodeSubmission, CodeSubmissionRecord


# 채점 인터페이스
class CodeJudgeInterface:
    """
    코드 채점 인터페이스.
    
    각 언어별로 구현해야 할 기본 채점 로직을 정의합니다.
    모든 하위 클래스는 이 인터페이스의 `run_code` 메서드를 구현해야 합니다.
    """

    def run_code(
        self, code: str, input_data: str, time_limit: int, memory_limit: int
    ) -> str:
        """
        제출된 코드를 실행하는 메서드. 하위 클래스에서 구현됩니다.

        Args:
            code (str): 실행할 코드.
            input_data (str): 코드에 제공할 입력 데이터.
            time_limit (int): 실행 제한 시간 (초 단위).
            memory_limit (int): 메모리 제한 (MB 단위).

        Returns:
            str: 실행 결과 또는 에러 메시지.
        """
        raise NotImplementedError("이 메서드는 서브클래스에서 구현되어야 합니다.")


class PythonCodeJudge(CodeJudgeInterface):
    """
    Python 코드 채점 로직을 구현하는 클래스.

    제출된 파이썬 코드를 주어진 시간과 메모리 제한 내에서 실행합니다.
    """

    def run_code(
        self, code: str, input_data: str, time_limit: int, memory_limit: int
    ) -> str:
        """
        제출된 파이썬 코드를 실행하고, 결과를 반환합니다.

        Windows와 Linux 환경에 따라 메모리 제한을 다르게 적용합니다.

        Args:
            code (str): 실행할 파이썬 코드.
            input_data (str): 코드에 제공할 입력 데이터.
            time_limit (int): 실행 제한 시간.
            memory_limit (int): 메모리 제한 (MB 단위).

        Returns:
            str: 실행 결과 또는 에러 메시지.
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


class JavaScriptCodeJudge(CodeJudgeInterface):
    """
    JavaScript (Node.js) 코드 채점 로직을 구현하는 클래스.

    제출된 자바스크립트 코드를 주어진 시간과 메모리 제한 내에서 실행합니다.
    """

    def run_code(
        self, code: str, input_data: str, time_limit: int, memory_limit: int
    ) -> str:
        """
        제출된 자바스크립트 코드를 실행하고, 결과를 반환합니다.

        Windows와 Linux 환경에 따라 메모리 제한을 다르게 적용합니다.

        Args:
            code (str): 실행할 자바스크립트 코드.
            input_data (str): 코드에 제공할 입력 데이터.
            time_limit (int): 실행 제한 시간.
            memory_limit (int): 메모리 제한 (MB 단위).

        Returns:
            str: 실행 결과 또는 에러 메시지.
        """
        try:
            with open("temp.js", "w") as f:
                f.write(code)

            if os.name == "nt":
                result = subprocess.run(
                    ["node", "temp.js"],
                    input=input_data.encode(),
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
                    ["node", "temp.js"],
                    input=input_data.encode(),
                    capture_output=True,
                    text=True,
                    timeout=time_limit,
                    preexec_fn=set_memory_limit,
                )

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            return "시간 초과"
        except Exception as e:
            return f"실행 에러: {e}"


class CodeJudgeFactory:
    """
    프로그래밍 언어에 따른 채점 클래스를 반환하는 팩토리 클래스.
    
    파이썬 또는 자바스크립트 코드 채점 클래스를 생성합니다.
    """

    @staticmethod
    def get_judge(language: str) -> CodeJudgeInterface:
        """
        언어에 맞는 채점 클래스를 반환합니다.

        Args:
            language (str): 'python' 또는 'javascript' 중 하나의 언어.

        Returns:
            CodeJudgeInterface: 해당 언어의 채점 클래스.

        Raises:
            ValueError: 지원하지 않는 언어인 경우 발생.
        """
        if language == "python":
            return PythonCodeJudge()
        elif language == "javascript":
            return JavaScriptCodeJudge()
        else:
            raise ValueError(f"지원하지 않는 언어입니다: {language}")


def evaluate_code_submission(
    code_submission: CodeSubmission,
    submitted_code: str,
    user,
    time_limit: int,
    memory_limit: int,
) -> dict:
    """
    제출된 코드를 채점하고, 채점 결과를 반환하는 함수.

    Args:
        code_submission (CodeSubmission): 채점할 코드 제출 정보.
        submitted_code (str): 제출된 코드.
        user (User): 제출한 사용자.
        time_limit (int): 실행 시간 제한.
        memory_limit (int): 메모리 제한.

    Returns:
        dict: 채점 결과 (전체 통과 여부 및 각 테스트 케이스 결과).
    """
    judge = CodeJudgeFactory.get_judge(code_submission.language)
    test_cases = [(code_submission.example_input, code_submission.example_output)]

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

    CodeSubmissionRecord.objects.create(
        user=user,
        code_submission=code_submission,
        submitted_code=submitted_code,
        test_results=str(results),
        is_passed=all_passed,
    )

    return {"all_passed": all_passed, "results": results}
