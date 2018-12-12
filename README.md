# dotbot-vscode
Plugin for [dotbot](https://github.com/anishathalye/dotbot). dotbot-vscode adds two directives: `vscode` and `vscodefile` to dotbot, which allows you to install、uninstall or sync your vscode extensions between multi places.

## Installation
1. Add this plugin to your dotfiles repository as a git submodule
    `git submodule add https://github.com/hujianxin/dotbot-vscode`
2. Add `vsocde` or `vscodefile` directive to your config file
3. Edit you `install` script to change like this `"${BASEDIR}/${DOTBOT_DIR}/${DOTBOT_BIN}" -d "${BASEDIR}" --plugin-dir dotbot-vscode -c "${CONFIG}" "${@}"`

## Detail
This is an example file.
```yaml
- vscode:
    dbaeumer.vscode-eslint: install
    eamodio.gitlens: uninstall
    eg2.tslint:

- vscodefile: Vscodefile

- vscodefile:
    - Vscodefile1
    - Vscodefile2

- vscodefile: [Vscodefile3, Vscodefile4]
```
For `vscode` directive, you ought to specify the operation to install or uninstall, default is install.

For `vscodefile` directive, you ought to generate a vscodefile using `code --list-extensions > $DIR/vscodefile` command.

In other place, you run `./install -p dotbot-vscode/vscode.py -c vscode.packages.conf.yaml`, `dotbot-vscode` will uninstall the extensions which are installed but not in `vscodefile`, and install the extensions which are not installed but in `vscodefile`.

