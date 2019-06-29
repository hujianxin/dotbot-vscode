# coding: utf-8
import os
import sys
import dotbot

from subprocess import check_output, call


sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib", "whichcraft")
)

from whichcraft import which


class VSCode(dotbot.Plugin):
    DIRECTIVE_VSCODE = "vscode"
    DIRECTIVE_VSCODE_FILE = "vscodefile"

    def can_handle(self, directive):
        return directive in (self.DIRECTIVE_VSCODE, self.DIRECTIVE_VSCODE_FILE)

    def handle(self, directive, data):
        if directive == self.DIRECTIVE_VSCODE_FILE:
            return self._handle_vscodefile(data)
        elif directive == self.DIRECTIVE_VSCODE:
            return self._handle_vscode(data)

    def _handle_vscodefile(self, data):
        if not isinstance(data, dict) or len(data) > 2:
            self._log.error("Error format, please refer to documentation.")
            return False
        elif len(data) == 2 and ("file" not in data or "insiders" not in data):
            self._log.error("Error format, please refer to documentation.")
            return False
        elif "file" not in data:
            self._log.error("Error format, please refer to documentation.")
            return False

        if "insiders" not in data:
            insiders = False
        else:
            insiders = data["insiders"]
        code = VSCodeInstance(insiders)
        vsfile = data["file"]
        return self._sync_vscodefile(vsfile, code)

    def _handle_vscode(self, data):
        if not isinstance(data, dict):
            self._log.error("Error format, please refer to documentation.")
            return False
        for extension in data:
            extension_status = data[extension]
            if not isinstance(extension_status, dict) or len(extension_status) > 2:
                self._log.error("Error format, please refer to documentation.")
                return False
            elif len(extension_status) == 2 and (
                "status" not in extension_status or "insiders" not in extension_status
            ):
                self._log.error("Error format, please refer to documentation.")
                return False
            elif "status" not in extension_status:
                self._log.error("Error format, please refer to documentation.")
                return False

            if "insiders" not in extension_status:
                insiders = False
            else:
                insiders = extension_status["insiders"]
            code = VSCodeInstance(insiders)
            try:
                if extension_status["status"] == "install":
                    code.install(extension)
                elif extension_status["status"] == "uninstall":
                    code.uninstall(extension)
                else:
                    self._log.error("Error format, please refer to documentation.")
                    return False
            except VSCodeError as e:
                self.log.error(e.message)
                return False
        return True

    def _vscodefile_extensions(self, vsfile):
        try:
            with open(vsfile) as f:
                result = [e.strip().lower() for e in f.readlines()]

        except FileNotFoundError:
            self._log.error("Can not find vscodefile: {}".format(vsfile))
            return None

        return result

    def _sync_vscodefile(self, vsfile, code):
        vscodefile_extensions = self._vscodefile_extensions(vsfile)

        if not vscodefile_extensions:
            return False

        need_install, need_remove = [], []
        try:
            installed_extensions = code.installed_extensions()
            for extension in installed_extensions:
                if extension.lower() not in vscodefile_extensions:
                    need_remove.append(extension)

            for extension in vscodefile_extensions:
                if extension.lower() not in installed_extensions:
                    need_install.append(extension)

            for extension in need_install:
                code.install(extension)

            for extension in need_remove:
                code.uninstall(extension)
        except VSCodeError as e:
            self._log.error(e.message)
            return False
        return True


class VSCodeInstance(object):
    def __init__(self, insiders=False):
        if not insiders:
            self._name = "Visual Studio Code"
            self._binary = which("code")
        else:
            self._name = "Visual Studio Code Insiders"
            self._binary = which("code-insiders")

    @property
    def installed(self):
        return self._binary is not None

    def installed_extensions(self):
        if not self.installed:
            raise VSCodeError("{} is not installed.".format(self._name))
        output = check_output([self._binary, "--list-extensions"]).decode(
            sys.getdefaultencoding()
        )

        return set(line.lower() for line in output.splitlines())

    def install(self, extension):
        if not self.installed:
            raise VSCodeError("{} is not installed.".format(self._name))
        call([self._binary, "--install-extension", extension])

    def uninstall(self, extension):
        if not self.installed:
            raise VSCodeError("{} is not installed.".format(self._name))
        call([self._binary, "--uninstall-extension", extension])


class VSCodeError(Exception):
    def __init__(self, message):
        self.message = message
