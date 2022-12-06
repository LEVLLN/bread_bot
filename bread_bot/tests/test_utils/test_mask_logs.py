import unittest

from bread_bot.utils.helpers import mask_string


class MaskLogsTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases_password = [
            '"password":"secret11111111"',
            '"password": "secret111112"',
            '"password":"secret111113"',
            '"password": "secret111114"',
            '"password":"secret111115"',
            '"password": "secret111116"',
            '"password":"secret111117"',
            '"password": "secret111118"',
            "password:secret111119",
            "password: secret111120",
            'password:"secret111121"',
            'password:"secret111122"',
            '"password":secret111123',
        ]
        cls.cases_result_password = [
            '"password":"***"',
            '"password": "***"',
            '"password":"***"',
            '"password": "***"',
            '"password":"***"',
            '"password": "***"',
            '"password":"***"',
            '"password": "***"',
            "password:***",
            "password: ***",
            'password:"***"',
            'password:"***"',
            '"password":***',
        ]
        cls.cases_email = [
            '"email":"secret21111111"',
            '"email": "secret21111112"',
            '"email":"secret21111113"',
            '"email": "secret21111114"',
            '"email":"secret21111115"',
            '"email": "secret21111116"',
            '"email":"secret21111117"',
            '"email": "secret21111118"',
            "email:secret21111119",
            "email: secret21111120",
            'email:"secret21111121"',
            'email:"secret21111121"',
            '"email":secret21111122',
        ]
        cls.cases_result_email = [
            '"email":"***"',
            '"email": "***"',
            '"email":"***"',
            '"email": "***"',
            '"email":"***"',
            '"email": "***"',
            '"email":"***"',
            '"email": "***"',
            "email:***",
            "email: ***",
            'email:"***"',
            'email:"***"',
            '"email":***',
        ]
        cls.cases_no_sensitives = [
            '"no_sensitive_data":"no_secret21111111"',
            '"no_sensitive_data": "no_secret21111112"',
            '"no_sensitive_data":"no_secret21111113"',
            '"no_sensitive_data": "no_secret21111114"',
            '"no_sensitive_data":"no_secret21111115"',
            '"no_sensitive_data": "no_secret21111116"',
            '"no_sensitive_data":"no_secret21111117"',
            '"no_sensitive_data": "no_secret21111118"',
            "no_sensitive_data:no_secret21111119",
            "no_sensitive_data: no_secret21111120",
            'no_sensitive_data:"no_secret21111121"',
            'no_sensitive_data:"no_secret21111121"',
            '"no_sensitive_data":no_secret21111122',
        ]
        cls.cases_cookie_header = [
            '"csrftoken"="secret31111111"',
            '"csrftoken"= "secret31111112"',
            '"csrftoken"="secret31111113"',
            '"csrftoken"= "secret31111114"',
            '"csrftoken"="secret31111115"',
            '"csrftoken"= "secret31111116"',
            '"csrftoken"="secret31111117"',
            '"csrftoken"= "secret31111118"',
            "csrftoken=secret31111119",
            "csrftoken= secret31111120",
            'csrftoken="secret31111121"',
            'csrftoken="secret31111121"',
            '"csrftoken"=secret31111122',
        ]
        cls.cases_result_cookie_header = [
            '"csrftoken"="***"',
            '"csrftoken"= "***"',
            '"csrftoken"="***"',
            '"csrftoken"= "***"',
            '"csrftoken"="***"',
            '"csrftoken"= "***"',
            '"csrftoken"="***"',
            '"csrftoken"= "***"',
            "csrftoken=***",
            "csrftoken= ***",
            'csrftoken="***"',
            'csrftoken="***"',
            '"csrftoken"=***',
        ]
        cls.logs = ",".join(
            cls.cases_password + cls.cases_email + cls.cases_cookie_header + cls.cases_no_sensitives,
        )
        cls.result_logs = ",".join(
            cls.cases_result_password
            + cls.cases_result_email
            + cls.cases_result_cookie_header
            + cls.cases_no_sensitives,
        )

    async def test_masking_logs(self):
        self.assertEqual(mask_string(self.logs), self.result_logs)

    async def test_additional_keys_masking_logs(self):
        self.assertEqual(
            mask_string(
                source_string=self.logs + '{"my_custom_key":"some_password"}', additional_mask_keys=("my_custom_key",)
            ),
            self.result_logs + '{"my_custom_key":"***"}',
        )

    async def test_additional_values_masking_logs(self):
        self.assertEqual(
            mask_string(
                source_string=self.logs + '{"some_key":"my_sensitive_value"}',
                additional_mask_values=("my_sensitive_value",),
            ),
            self.result_logs + '{"some_key":"***"}',
        )
