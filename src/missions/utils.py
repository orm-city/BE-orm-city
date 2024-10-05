import ast

def evaluate_code(submitted_code, test_cases):
    total_cases = len(test_cases)
    passed_cases = 0

    # 제출된 코드를 AST로 파싱하여 안전한 코드만 실행
    try:
        tree = ast.parse(submitted_code, mode='exec')
        code_object = compile(tree, filename="<ast>", mode="exec")
    except SyntaxError:
        return 0  # 구문 오류인 경우 0점 처리

    for case in test_cases:
        try:
            # 안전한 네임스페이스에서 코드 실행
            exec_namespace = {}
            exec(code_object, {'__builtins__': {}}, exec_namespace)

            # 함수 이름 추출 (여기서는 단일 함수가 정의되어 있다고 가정)
            function_name = [name for name in exec_namespace if not name.startswith('__')][0]
            func = exec_namespace[function_name]

            # 테스트 케이스 실행
            input_data = case['input']
            expected_output = case['expected_output']

            result = func(*input_data)

            if result == expected_output:
                passed_cases += 1

        except Exception:
            continue  # 예외 발생 시 해당 테스트 케이스는 실패 처리

    # 점수 계산
    if total_cases == 0:
        return 0
    score = (passed_cases / total_cases) * 100  # 100점 만점 기준
    return score
