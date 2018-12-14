# coding: utf-8
import sys
import shutil
import dotbot

from subprocess import check_output, call


class VSCode(dotbot.Plugin):
    DIRECTIVE_VSCODE = "vscode"
    DIRECTIVE_VSCODE_FILE = "vscodefile"

    def can_handle(self, directive):
        self.__code = shutil.which("code")
        self.__code_insiders = shutil.which("code-insiders")
        return directive in (self.DIRECTIVE_VSCODE, self.DIRECTIVE_VSCODE_FILE)

    def handle(self, directive, data):
        res = True
        if directive == self.DIRECTIVE_VSCODE_FILE:
            res = self._handle_vscodefile(data)
        elif directive == self.DIRECTIVE_VSCODE:
            res = self._handle_vscode(data)
        return res

    def _handle_vscodefile(self, data):
        if not isinstance(data, dict) or len(data) > 2:
            raise VSCodeError("Error format, please refer to documentation.")
        elif len(data) == 2 and ("file" not in data or "insiders" not in data):
            raise VSCodeError("Error format, please refer to documentation.")
        elif "file" not in data:
            raise VSCodeError("Error format, please refer to documentation.")

        if "insiders" not in data:
            insiders = False
        else:
            insiders = data["insiders"]
        f = data["file"]
        return self._sync_vscodefile(f, insiders)

    def _handle_vscode(self, data):
        if not isinstance(data, dict):
            self._log.error("Error format, please refer to documentation.")
            return False
        result = False
        for extension_dict in data:
            if not extension_dict or len(extension_dict) != 1:
                raise VSCodeError("Error format, please refer to documentation.")
            tmp = extension_dict.popitem()
            extension_name = tmp[0]
            extension_status = tmp[1]
            if not isinstance(extension_status, dict) or len(extension_status) > 2:
                raise VSCodeError("Error format, please refer to documentation.")
            elif len(extension_status) == 2 and (
                "status" not in extension_status or "insiders" not in extension_status
            ):
                raise VSCodeError("Error format, please refer to documentation.")
            elif "status" not in extension_status:
                raise VSCodeError("Error format, please refer to documentation.")
            status = extension_status["status"]
            if "insiders" not in extension_status:
                insiders = False
            else:
                insiders = data["insiders"]
            if status == "install":
                self._install(extension_name, insiders)
                result = True
            elif status == "uninstall":
                self._uninstall(extension_name, insiders)
                result = True
            else:
                result = False
                self._log.error("Error operation, please refer to documentation.")
        return result

    def _install(self, extension, insiders):
        if insiders:
            if self.__code_insiders:
                call([self.__code_insiders, "--install-extension", extension])
            else:
                raise VSCodeError(
                    "{} is not be \
                        installed.".format(
                        self.__code_insiders
                    )
                )
        else:
            if self.__code:
                call([self.__code, "--install-extension", extension])
            else:
                raise VSCodeError(
                    "{} is not be \
                        installed.".format(
                        self.__code
                    )
                )

    def _uninstall(self, extension, insiders):
        if insiders:
            if self.__code_insiders:
                call([self.__code_insiders, "--uninstall-extension", extension])
            else:
                raise VSCodeError(
                    "{} is not be \
                        installed.".format(
                        self.__code_insiders
                    )
                )
        else:
            if self.__code:
                call([self.__code, "--uninstall-extension", extension])
            else:
                raise VSCodeError(
                    "{} is not be \
                        installed.".format(
                        self.__code
                    )
                )

    def _installed_extensions(self, insiders):
        output = check_output([self.__code, "--list-extensions"]).decode(
            sys.getdefaultencoding()
        )
        if insiders:
            if self.__code_insiders:
                call([self.__code_insiders, "--list-extensions"])
            else:
                raise VSCodeError(
                    "{} is not be \
                        installed.".format(
                        self.__code_insiders
                    )
                )
        else:
            if self.__code:
                call([self.__code, "--list-extensions"])
            else:
                raise VSCodeError(
                    "{} is not be \
                        installed.".format(
                        self.__code
                    )
                )

        return set(line.lower() for line in output.splitlines())

    def _vscodefile_extensions(self, vsfile):
        try:
            with open(vsfile) as f:
                result = [e.strip().lower() for e in f.readlines()]

        except FileNotFoundError:
            self._log.error("Can not find vscodefile: {}".format(vsfile))
            return None

        return result

    def _sync_vscodefile(self, vsfile, insiders):
        installed_extensions = self._installed_extensions(insiders)
        vscodefile_extensions = self._vscodefile_extensions(vsfile)

        if not vscodefile_extensions:
            return False

        need_install, need_remove = [], []
        try:
            for extension in installed_extensions:
                if extension.lower() not in vscodefile_extensions:
                    need_remove.append(extension)

            for extension in vscodefile_extensions:
                if extension.lower() not in installed_extensions:
                    need_install.append(extension)

            for extension in need_install:
                self._install(extension, insiders)

            for extension in need_remove:
                self._uninstall(extension, insiders)
        except Exception:
            return False
        return True


class VSCodeError(Exception):
    pass
