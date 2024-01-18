# import pytest
# from ipm.__main__ import main
# from unittest.mock import patch, MagicMock

# # Test IDs for parametrization
# HAPPY_PATH_INSTALL = "happy_install"
# HAPPY_PATH_EXTRACT = "happy_extract"
# HAPPY_PATH_BUILD = "happy_build"
# EDGE_CASE_NO_ARGS = "edge_no_args"
# ERROR_CASE_UNKNOWN_COMMAND = "error_unknown_command"

# # Mock the sys.argv to simulate command line arguments
# @pytest.fixture
# def mock_sys_argv(monkeypatch):
#     def _mock_sys_argv(args):
#         monkeypatch.setattr("sys.argv", ["ipm"] + args)
#     return _mock_sys_argv

# # Mock the api functions to prevent actual execution
# @pytest.fixture
# def mock_api_functions(monkeypatch):
#     install_mock = MagicMock()
#     extract_mock = MagicMock()
#     build_mock = MagicMock()
#     monkeypatch.setattr("ipm.__main__.install", install_mock)
#     monkeypatch.setattr("ipm.__main__.extract", extract_mock)
#     monkeypatch.setattr("ipm.__main__.build", build_mock)
#     return install_mock, extract_mock, build_mock

# @pytest.mark.parametrize("test_id, args, expected_call", [
#     # Happy path tests
#     (HAPPY_PATH_INSTALL, ["install", "http://ipm.hydroroll.team/package.ipk"], ("install", ["http://ipm.hydroroll.team/package.ipk", None])),
#     (HAPPY_PATH_EXTRACT, ["extract", "package.ipk", "--dist", "dist_folder"], ("extract", ["package.ipk", "dist_folder"])),
#     (HAPPY_PATH_BUILD, ["build", "source_folder"], ("build", ["source_folder"])),
    
#     # Edge case tests
#     (EDGE_CASE_NO_ARGS, [], ("help", [])),
    
#     # Error case tests
#     (ERROR_CASE_UNKNOWN_COMMAND, ["unknown", "arg"], ("error", ["unknown"])),
# ])
# def test_main_commands(test_id, args, expected_call, mock_sys_argv, mock_api_functions, capsys):
#     mock_sys_argv(args)
#     install_mock, extract_mock, build_mock = mock_api_functions

#     # Act
#     with pytest.raises(SystemExit):  # argparse exits the program when -h is called or on error
#         main()

#     # Assert
#     if expected_call[0] == "install":
#         install_mock.assert_called_once_with(*expected_call[1], echo=True)
#     elif expected_call[0] == "extract":
#         extract_mock.assert_called_once_with(*expected_call[1])
#     elif expected_call[0] == "build":
#         build_mock.assert_called_once_with(*expected_call[1])
#     elif expected_call[0] == "help":
#         captured = capsys.readouterr()
#         assert "Infini 包管理器" in captured.out
#     elif expected_call[0] == "error":
#         captured = capsys.readouterr()
#         assert "error: unrecognized arguments" in captured.err

# pytest.main()