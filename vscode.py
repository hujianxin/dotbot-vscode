import os
import sys
import shutil
import dotbot

from subprocess import check_output, check_call


class VSCode(dotbot.Plugin):
    DIRECTIVE_VSCODE = "vscode"
    DIRECTIVE_VSCODE_FILE = "vscodefile"

    def can_handle(self, directive):
        self.__code = shutil.which("code")
        exists = True if self.__code else False

        return exists and (
            directive in (self.DIRECTIVE_VSCODE, self.DIRECTIVE_VSCODE_FILE)
        )

    def handle(self, directive, data):
        if directive == self.DIRECTIVE_VSCODE_FILE:
            self._sync(data)
        elif directive == self.DIRECTIVE_VSCODE:
            pass

    def _install(self, extension):
        check_call([self.__code, "--install-extension", extension])

    def _uninstall(self, extension):
        check_call([self.__code, "--uninstall-extension", extension])

    def _installed_extensions(self):
        output = check_output([self.__code, "--list-extensions"]).decode(
            sys.getdefaultencoding()
        )

        return set(line.lower() for line in output.splitlines())

    def _vscodefile_extensions(self, vsfile):
        try:
            with open(vsfile) as f:
                result = [e.strip().lower() for e in f.readlines()]

        except FileNotFoundError:
            self._log.info("Can not find vscodefile: {}".format(vsfile))
            return None
        return result

    def _sync(self, vsfile):
        installed_extensions = self._installed_extensions()

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
                self._install(extension)

            for extension in need_remove:
                self._uninstall(extension)
        except Exception:
            return False
        return True
