"""
测试模块: {{MODULE_NAME}}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# 导入被测模块
# from {{module_path}} import {{ClassName}}, {{function_name}}


class Test{{ClassName}}:
    """{{ClassName}} 的测试类"""

    @pytest.fixture
    def instance(self):
        """创建被测实例"""
        return {{ClassName}}()

    # ==================== 正常路径测试 ====================

    def test_{{method_name}}_with_valid_input_returns_expected(self, instance):
        """测试正常输入返回预期结果"""
        # Arrange
        input_data = ...
        expected = ...

        # Act
        result = instance.{{method_name}}(input_data)

        # Assert
        assert result == expected

    # ==================== 边界情况测试 ====================

    def test_{{method_name}}_with_empty_input_returns_default(self, instance):
        """测试空输入返回默认值"""
        # Arrange
        input_data = None  # 或 [], "", {}

        # Act
        result = instance.{{method_name}}(input_data)

        # Assert
        assert result == ...  # 默认值或空值

    def test_{{method_name}}_with_max_value_handles_correctly(self, instance):
        """测试最大值边界"""
        # Arrange
        input_data = ...  # 最大值

        # Act
        result = instance.{{method_name}}(input_data)

        # Assert
        assert result == ...

    # ==================== 异常情况测试 ====================

    def test_{{method_name}}_with_invalid_input_raises_error(self, instance):
        """测试无效输入抛出异常"""
        # Arrange
        invalid_input = ...

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            instance.{{method_name}}(invalid_input)

        assert "expected error message" in str(excinfo.value)

    # ==================== Mock 测试 ====================

    @patch('{{module_path}}.external_dependency')
    def test_{{method_name}}_calls_external_service(self, mock_dep, instance):
        """测试外部依赖调用"""
        # Arrange
        mock_dep.return_value = "mocked_response"

        # Act
        result = instance.{{method_name}}(...)

        # Assert
        mock_dep.assert_called_once_with(...)
        assert result == ...


# ==================== 函数测试 ====================

class TestFunctionName:
    """{{function_name}} 的测试"""

    @pytest.mark.parametrize("input_val,expected", [
        (1, 2),
        (2, 4),
        (0, 0),
        (-1, -2),
    ])
    def test_function_with_various_inputs(self, input_val, expected):
        """参数化测试多种输入"""
        result = {{function_name}}(input_val)
        assert result == expected
