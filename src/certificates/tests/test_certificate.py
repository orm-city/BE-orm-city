import pytest
from certificates.services import encrypt_certificate_data, decrypt_certificate_data


# 고정된 테스트 데이터를 사용할 때 pytest fixture를 사용하여 설정할 수 있습니다.
@pytest.fixture
def test_data():
    return "Test Certificate Data"


# 암호화 테스트
def test_encrypt_decrypt_certificate_data(test_data):
    # 수료증 데이터를 암호화
    encrypted_data = encrypt_certificate_data(test_data)

    # 암호화된 데이터를 복호화
    decrypted_data = decrypt_certificate_data(encrypted_data)

    # 원본 데이터와 복호화된 데이터가 같은지 확인
    assert (
        test_data == decrypted_data
    ), "암호화 후 복호화된 데이터가 원본과 일치하지 않습니다."
